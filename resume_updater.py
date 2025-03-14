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

# Pydantic models for structured data
class ResumeContent(BaseModel):
    personal_info: dict
    experience: List[dict]
    projects: List[dict]
    skills: List[str]
    education: List[dict]

class JobPostingDetails(BaseModel):
    title: str
    required_skills: List[str]
    preferred_skills: List[str]
    responsibilities: List[str]

# Initialize app
app = MCPApp(name="resume_updater")

async def update_resume(
    resume_path: str,
    github_repos: List[str],
    job_posting_url: str,
    job_description_path: str,
    output_path: str
):
    async with app.run() as mcp_agent_app:
        logger = mcp_agent_app.logger

        # Define agents
        pdf_agent = Agent(
            name="pdf_reader",
            instruction="Convert PDF to markdown and extract content.",
            server_names=["filesystem", "markdownify"]
        )

        github_agent = Agent(
            name="repo_analyzer",
            instruction="Analyze GitHub repos and extract relevant project details",
            server_names=["fetch", "filesystem"]
        )

        job_agent = Agent(
            name="job_analyzer", 
            instruction="Extract key requirements and details from job posting. You can find additional information in the provided txt file.",
            server_names=["fetch", "filesystem"]
        )

        # Process each agent sequentially
        async with pdf_agent, github_agent, job_agent:
            pdf_llm = await pdf_agent.attach_llm(OpenAIAugmentedLLM)
            github_llm = await github_agent.attach_llm(OpenAIAugmentedLLM)
            job_llm = await job_agent.attach_llm(OpenAIAugmentedLLM)

            # Execute agents
            pdf_content = await pdf_llm.generate_str(f"Read and parse resume from {resume_path}", request_params=RequestParams(model="gpt-4o-mini"))
            repo_content = await github_llm.generate_str(f"Analyze repos: {', '.join(github_repos)}", request_params=RequestParams(model="gpt-4o-mini"))
            job_content = await job_llm.generate_str(f"Analyze job posting at {job_posting_url}. Additional job description can be found here: {job_description_path}", request_params=RequestParams(model="gpt-4o-mini"))

        # Manually aggregate results
        aggregated_results = {
            "resume_content": pdf_content,
            "github_projects": repo_content,
            "job_requirements": job_content
        }

        # Create optimizer and evaluator agents
        optimizer = Agent(
            name="resume_optimizer",
            instruction="Generate optimized resume content targeting the job requirements",
            server_names=["filesystem"]
        )

        evaluator = Agent(
            name="resume_evaluator",
            instruction="""Evaluate resume for:
            1. Relevance to job requirements
            2. Clear demonstration of skills
                a. The order of skills and experience should list most relevant first
            3. Length (must fit one page)
            4. Professional formatting""",
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
        Aggregated Analysis: {aggregated_results}
        
        Generate an optimized one-page resume targeting this job position. Try to match the format and style of the original resume.
        Do NOT include any technologies or libraries that are not explicitly mentioned in the current resume or github projects.
        """

        final_resume = await eo_workflow.generate_str(optimization_prompt, request_params=RequestParams(model="gpt-4o-mini"))

        # Write final resume to PDF
        write_agent_pdf = Agent(
            name="pdf_writer",
            instruction="Convert content to PDF format",
            server_names=["filesystem", "mcp-pandoc"]
        )

        write_agent = Agent(
            name="resume_writer",
            instruction="Write content to markdown file",
            server_names=["filesystem"]
        )
        
        async with write_agent:
            llm = await write_agent.attach_llm(OpenAIAugmentedLLM)
            await llm.generate_str(
                f"Write the following content to {output_path}: {final_resume}",
                request_params=RequestParams(model="gpt-4o-mini")
            )

        logger.info(f"Updated resume written to {output_path}")

# Main execution
async def main():
    await update_resume(
        resume_path="/home/bnoffke/Documents/Resume/current_resume.pdf",
        github_repos=[
            "https://github.com/bnoffke/resume_updater",
            "https://github.com/bnoffke/llm_scripting"
        ],
        job_posting_url="https://careers-uwcu.icims.com/jobs/5730/ai-engineer/job",
        job_description_path="/home/bnoffke/Documents/Resume/job_description.txt",
        output_path="/home/bnoffke/Documents/Resume/tailored_resume.txt"
    )
async def main(
    resume_path="/home/bnoffke/Documents/Resume/current_resume.pdf",
        github=[
            "https://github.com/bnoffke/resume_updater",
            "https://github.com/bnoffke/llm_scripting"
        ],
        job_posting_url="https://careers-uwcu.icims.com/jobs/5730/ai-engineer/job",
        job_description_path="/home/bnoffke/Documents/Resume/job_description.txt",
        output_path="/home/bnoffke/Documents/Resume/tailored_resume.txt"
    ):
    await update_resume(
        resume_path=resume_path,
        github_repos=github,
        job_posting_url=job_posting_url,
        job_description_path=job_description_path,
        output_path=output_path
    )
if __name__ == "__main__":
    asyncio.run(main())