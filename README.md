# resume_updater

An AI-powered tool that automatically tailors your resume for specific job applications using the Model Context Protocol (MCP) agent framework.

## Project Overview

This tool analyzes your current resume, GitHub repositories, and a job posting to generate a tailored resume that highlights relevant skills and experiences for the target position.

### Approach

1. **Input Processing**
   - Reads and parses existing resume from PDF
   - Analyzes specified GitHub repositories for project details
   - Extracts requirements from job posting URL and description file

2. **Content Optimization**
   - Aggregates information from all sources
   - Uses an evaluator-optimizer workflow to generate optimized content
   - Ensures output maintains professional formatting and fits one page

3. **Quality Control**
   - Evaluates resume for relevance to job requirements
   - Verifies clear demonstration of skills
   - Checks formatting and length constraints

4. **Output Generation**
   - Generates the final resume in markdown format
   - Converts to PDF using Pandoc

## Technologies Used

- **MCP Agent Framework**: Core orchestration system for AI agents
- **OpenAI GPT-4**: Powers the AI agents for content analysis and generation
- **MCP Servers**:
  - `fetch-mcp`: Handles URL content retrieval
  - `markdownify-mcp`: Converts between formats
  - `filesystem-mcp`: Manages file operations
  - `mcp-pandoc`: Handles PDF conversion

## Setup Instructions

### Python Dependencies
1. **Install Poetry** (if not already installed):
   Follow the instructions from the official [Poetry documentation](https://python-poetry.org/docs/#installation).

2. **Navigate to Your Project Directory:**
   ```bash
   cd /home/bnoffke/repos/resume_updater
   ```

3. **Install the Python Dependencies:**
   ```bash
   poetry install
   ```

### npm Dependencies
1. **Ensure Node.js and npm are Installed:**
   You can download and install them from [Node.js official website](https://nodejs.org/).

2. **Navigate to Your Project Directory:**
   ```bash
   cd /home/bnoffke/repos/resume_updater
   ```

3. **Install the npm Dependencies:**
   ```bash
   npm install
   ```

### Additional Requirements
1. **Install Pandoc**:
   Required for PDF conversion. Follow your system's package manager instructions.

## Usage

Run the script with default parameters:
```bash
poetry run python resume_updater.py
```

Or customize the parameters:
```python
await update_resume(
    resume_path="path/to/current_resume.pdf",
    github_repos=["repo1_url", "repo2_url"],
    job_posting_url="job_posting_url",
    job_description_path="path/to/description.txt",
    output_path="path/to/output.txt"
)
```