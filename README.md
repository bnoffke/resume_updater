# resume_updater

An AI-powered tool that automatically tailors your resume for specific job applications using the Model Context Protocol (MCP) agent framework.

## Project Overview

This tool analyzes your current resume, GitHub repositories, and a job posting to generate a tailored resume that highlights relevant skills and experiences for the target position.

### Approach

1. **Input Processing**
   - Reads and parses existing resume from PDF
   - Analyzes specified GitHub repositories for project details
   - Extracts requirements from job posting URL and description file
      - **Caveat**: The `fetch-mcp` server retrieves only web content present in HTML. To handle more complex content, such as JavaScript-rendered iFrames, additional MCP servers must be utilized.

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
   - Pauses to allow the user to review and tweak the tailored resume

## Technologies Used

- **MCP Agent Framework**: Core orchestration system for AI agents
- **OpenAI**: Powers the AI agents for content analysis and generation
- **MCP Servers**:
  - `fetch-mcp`: Handles URL content retrieval
  - `markdownify-mcp`: Converts between formats
  - `filesystem-mcp`: Manages file operations
  - `markdown2pdf-mcp`: Converts markdown to PDF format

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
1. **Setup markdown2pdf-mcp server**:
   - Clone the repository from [markdown2pdf-mcp](https://github.com/2b3pro/markdown2pdf-mcp)
   - Follow the installation instructions in the repository's README

## Usage

Run the script with default parameters:
```bash
poetry run python resume_updater.py
```

The script accepts the following parameters:

```python
await update_resume(
    resume_path="/home/bnoffke/Documents/Resume/current_resume.pdf",  # Path to your current resume PDF
    github_repos=[                                                    # List of GitHub repository URLs to analyze
        "https://github.com/username/repo1",
        "https://github.com/username/repo2"
    ],
    job_posting_url="https://example.com/job-posting",               # URL of the job posting
    job_description_path="/path/to/job_description.txt",             # Path to additional job description file
    output_path="/path/to/output/resume",                            # Output path and filename (without extension)
    additional_info="/path/to/additional_info.txt"                    # Optional: Path to file with additional information
)
```

### Parameter Details

- **resume_path**: Path to your current resume in PDF format
- **github_repos**: List of GitHub repository URLs that showcase relevant work
- **job_posting_url**: URL of the job posting to analyze
- **job_description_path**: Path to a text file containing additional job description details
- **output_path**: Base path for output files (will create both .md and .pdf)
- **additional_info**: Optional path to a text file containing additional information to incorporate

The script will:
1. Generate a markdown file at `{output_path}.md`
2. Pause for your review and modifications
3. Create the final PDF at `{output_path}.pdf` using markdown2pdf-mcp server