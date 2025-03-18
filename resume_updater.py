import asyncio
from pathlib import Path
from typing import List
from pydantic import BaseModel

from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from mcp_agent.workflows.evaluator_optimizer.evaluator_optimizer import (
    EvaluatorOptimizerLLM,
    QualityRating,
)
from mcp_agent.workflows.llm.augmented_llm import RequestParams
from resume_schema import Resume, Personal, Job

# Initialize app
app = MCPApp(name="resume_updater")

#Build request parameters, with options to specify a separate model for evaluator-optimizer
small_model_req_param = RequestParams(model="gpt-4o-mini")
eo_req_param = RequestParams(model="gpt-4o-mini")

async def update_resume(
    resume_path: str,
    github_repos: List[str],
    job_posting_url: str,
    job_description_path: str,
    output_path: str,
    additional_info: str = "",
):
    async with app.run() as mcp_agent_app:
        logger = mcp_agent_app.logger

        # Define agents
        job_agent = Agent(
            name="job_analyzer", 
            instruction="Extract key requirements and details from job posting. You can find additional information in the provided txt file.",
            server_names=["filesystem"]
        )

        additional_info_agent = Agent(
            name="info_reader",
            instruction="Read and extract content from additional information file.",
            server_names=["filesystem"]
        )

        pdf_agent = Agent(
            name="pdf_reader",
            instruction="Convert PDF to markdown and extract content.",
            server_names=["filesystem", "markdownify"]
        )

        

        github_agent = Agent(
            name="repo_analyzer",
            instruction="Analyze GitHub repos and extract the content of the README.md files. Use the provided job requirements to guide your analysis.",
            server_names=["fetch", "filesystem"]
        )


        # Process each agent sequentially
        async with pdf_agent, github_agent, job_agent, additional_info_agent:
            pdf_llm = await pdf_agent.attach_llm(OpenAIAugmentedLLM)
            github_llm = await github_agent.attach_llm(OpenAIAugmentedLLM)
            job_llm = await job_agent.attach_llm(OpenAIAugmentedLLM)
            info_llm = await additional_info_agent.attach_llm(OpenAIAugmentedLLM)

            # Execute job analysis first
            job_content = await job_llm.generate_str(
                f"Analyze job posting at {job_posting_url}. Additional job description can be found here: {job_description_path}",
                request_params=small_model_req_param
            )

            # Use job requirements to guide GitHub analysis
            repo_content = await github_llm.generate_str(
                f"""Using the following job requirements:
                {job_content}
                
                Analyze these repos focusing on relevant experience and skills, extracting information to be used in a resume: {', '.join(github_repos)}""",
                request_params=small_model_req_param
            )

            # Parse resume with structured output
            pdf_content = await pdf_llm.generate_structured(
                message=f"""Read and parse resume from {resume_path}.
                Extract and organize the information into a structured format with personal details and job history.""",
                response_model=Resume,
                request_params=small_model_req_param
            )

            # Process additional info
            additional_info_content = await info_llm.generate_str(
                f"Read and extract content from {additional_info}",
                request_params=small_model_req_param
            )

        # Manually aggregate results
        aggregated_results = {
            "resume_content": pdf_content.model_dump(),
            "github_projects": repo_content,
            "job_requirements": job_content,
            "additional_info": additional_info_content
        }

        # Create optimizer and evaluator agents
        optimizer = Agent(
            name="resume_optimizer",
            instruction="""
            You will receive the following information:
            1. Current resume content
            2. Github projects
            3. Job requirements
            4. Additional information
            Generate an optimized one-page resume.
            Using the current resume as a reference, update with relevant information and include relevant github projects with their summaries that target the job description.
            Use additional_information provided to enhance the resume.
            Avoid flowerly language.
            Be sure to include links for the github repos and use a human readable name as the text for the github link. Keep it concise by making the project title a link.
            Please remove any content that is not relevant to the job description.
            Do NOT fabricate outcomes like "decreasing report generation time by 30%.". Do NOT include any technologies or libraries that are not explicitly mentioned in the current resume or github projects.
            Return ONLY the content of the resume, in markdown format.
            """,
            server_names=["filesystem"]
        )

        evaluator = Agent(
            name="resume_evaluator",
            instruction=f"""Evaluate resume for:
            1. Relevance to job requirements:
                Job Requirements:
                {job_content}
            2. Using the information provided to include other information and format specifications:
                {additional_info_content}
            3. Clear demonstration of skills
                a. The order of skills and experience should list most relevant first
                b. Skills should align with the job requirements above
                c. Skills should incorporate relevant additional information provided
            4. Length (must fit one page)
            5. Professional formatting""",
            server_names=["filesystem"]
        )

        # Set up evaluator-optimizer workflow
        eo_workflow = EvaluatorOptimizerLLM(
            optimizer=optimizer,
            evaluator=evaluator,
            llm_factory=OpenAIAugmentedLLM,
            min_rating=QualityRating.EXCELLENT
        )

        # Use evaluator-optimizer workflow on the aggregated results
        optimization_prompt = f"""
        Generate an optimized one-page resume with the following context: {aggregated_results}
        """

        final_resume = await eo_workflow.generate_str(optimization_prompt, request_params=eo_req_param)


        write_agent = Agent(
            name="resume_writer",
            instruction="Write content to markdown file",
            server_names=["filesystem"]
        )

        
        async with write_agent:
            llm = await write_agent.attach_llm(OpenAIAugmentedLLM)
            await llm.generate_str(
                f"Write the following content to {output_path}.md: {final_resume}",
                request_params=small_model_req_param
            )

        #Prompt user to review the resume at {output_path}.md then hit enter to continue. Do this by writing to the console.
        message = f"Please review the resume at {output_path}.md then hit enter to continue when you've finished making changes."
        width = len(message) + 4
        print("╔" + "═" * width + "╗")
        print("║  " + message + "  ║")
        print("╚" + "═" * width + "╝")
        input()


        # Write final resume to PDF
        write_agent_pdf = Agent(
            name="pdf_writer",
            instruction="Convert content to PDF format",
            server_names=["filesystem", "markdown2pdf"]
        )
        
        # Use write_agent_pdf to convert the txt to pdf, with explicity paths
        async with write_agent_pdf:
            llm = await write_agent_pdf.attach_llm(OpenAIAugmentedLLM)
            await llm.generate_str(
                f"Place the content of {output_path}.md into a string, then convert the markdown string to PDF format and save it as tailored_resume.pdf",
                request_params=small_model_req_param
            )

        logger.info(f"Updated resume written to {output_path}.pdf")

# Main execution
async def main(
    resume_path="/home/bnoffke/Documents/Resume/current_resume.pdf",
        github=[
            "https://github.com/bnoffke/resume_updater",
            "https://github.com/bnoffke/llm_scripting"
        ],
        job_posting_url="https://careers-uwcu.icims.com/jobs/5730/ai-engineer/job",
        job_description_path="/home/bnoffke/Documents/Resume/job_description.txt",
        output_path="/home/bnoffke/Documents/Resume/tailored_resume",
        additional_info="/home/bnoffke/Documents/Resume/additional_info.txt",
    ):
    await update_resume(
        resume_path=resume_path,
        github_repos=github,
        job_posting_url=job_posting_url,
        job_description_path=job_description_path,
        output_path=output_path,
        additional_info=additional_info,
    )
if __name__ == "__main__":
    asyncio.run(main())