import asyncio
from pathlib import Path
from typing import List
from pydantic import BaseModel

from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from mcp_agent.workflows.parallel.parallel_llm import ParallelLLM
from mcp_agent.workflows.evaluator_optimizer.evaluator_optimizer import (
    EvaluatorOptimizerLLM,
    QualityRating,
)

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
    output_path: str
):
    async with app.run() as mcp_agent_app:
        logger = mcp_agent_app.logger

        # Define agents
        pdf_agent = Agent(
            name="pdf_reader",
            instruction="Extract structured content from PDF resume",
            server_names=["filesystem", "mcp-pandoc"]
        )

        github_agent = Agent(
            name="repo_analyzer",
            instruction="Analyze GitHub repos and extract relevant project details",
            server_names=["fetch", "filesystem"]
        )

        job_agent = Agent(
            name="job_analyzer", 
            instruction="Extract key requirements and details from job posting",
            server_names=["fetch"]
        )

        # Set up parallel workflow
        parallel = ParallelLLM(
            fan_out_agents=[pdf_agent, github_agent, job_agent],
            llm_factory=OpenAIAugmentedLLM
        )

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

        # Execute parallel analysis
        inputs = {
            "pdf_reader": f"Read and parse resume from {resume_path}",
            "repo_analyzer": f"Analyze repos: {', '.join(github_repos)}",
            "job_analyzer": f"Analyze job posting at {job_posting_url}"
        }
        
        parallel_results = await parallel.generate_structured(
            message=inputs,
            output_model=ResumeContent
        )

        # Generate optimized resume
        optimization_prompt = f"""
        Original Resume: {parallel_results.pdf_reader}
        GitHub Projects: {parallel_results.repo_analyzer}
        Job Requirements: {parallel_results.job_analyzer}
        
        Generate an optimized one-page resume targeting this job position.
        """

        final_resume = await eo_workflow.generate_str(optimization_prompt)
        
        # Write final resume to PDF
        write_agent = Agent(
            name="pdf_writer",
            instruction="Convert content to PDF format",
            server_names=["filesystem", "mcp-pandoc"]
        )
        
        async with write_agent:
            llm = await write_agent.attach_llm(OpenAIAugmentedLLM)
            await llm.generate_str(
                f"Write the following content to {output_path}: {final_resume}"
            )

        logger.info(f"Updated resume written to {output_path}")

# Main execution
async def main():
    await update_resume(
        resume_path="/home/bnoffke/Documents/Resume/current_resume.pdf",
        github_repos=[
            "https://github.com/user/repo1",
            "https://github.com/user/repo2"
        ],
        job_posting_url="https://example.com/job-posting",
        output_path="/home/bnoffke/Documents/Resume/tailored_resume.pdf"
    )

if __name__ == "__main__":
    asyncio.run(main())