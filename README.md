# resume_updater

An AI-powered tool that automatically tailors your resume for specific job applications using the Model Context Protocol (MCP) agent framework.

## Project Overview

This tool analyzes your current resume, GitHub repositories, and a job posting to generate a tailored resume that highlights relevant skills and experiences for the target position.

### Future

1. **Enhanced Web Scraping**
   - Implement advanced web scraping capabilities to handle JavaScript-rendered content and iframes
   - Explore integration with tools like Selenium or Playwright for dynamic content retrieval

2. **Interactive User Interface**
   - Develop a Streamlit-based chat interface for a more intuitive user experience
   - Provide GUI-based configuration of input.json as an alternative to manual editing
   - Enable real-time resume previews and adjustments

3. **HTML-Based Resume Generation**
   - Pivot from Markdown to HTML for greater control over formatting
   - Implement custom CSS styling for precise layout management
   - Maintain clean, semantic markup for accessibility

4. **Page Length Optimization**
   - Integrate PDF page length validation into the evaluator-optimizer workflow
   - Add automated font size and margin adjustments while preserving readability

### Approach

1. **Input Processing**
   - Reads and parses existing resume from PDF
   - Analyzes specified GitHub repositories for project details
   - Extracts requirements from job posting URL and description file
      - **Caveat**: The `fetch-mcp` server retrieves only web content present in HTML. To handle more complex content, such as JavaScript-rendered iFrames, additional MCP servers must be utilized in the future.

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

### Install pnpm
1. **Install pnpm** (required for some dependencies):
   ```bash
   npm install -g pnpm
   ```
   Or follow alternative installation methods from the [pnpm documentation](https://pnpm.io/installation).

### Additional Requirements
1. **Setup markdown2pdf-mcp server**:
   - Clone the repository from [markdown2pdf-mcp](https://github.com/2b3pro/markdown2pdf-mcp)
   - Follow the installation instructions in the repository's README

2. **Setup markdownify-mcp server**:
   - Clone the repository from [markdownify-mcp](https://github.com/zcaceres/markdownify-mcp)
   - Install dependencies: `pnpm install`
   - Build the project: `pnpm run build`

3. **Setup fetch-mcp server**:
   - Clone the repository from [fetch-mcp](https://github.com/zcaceres/fetch-mcp)
   - Install dependencies: `npm install`
   - Build the project: `npm run build`

4. **Configure MCP Servers**
   Use the provided `mcp_agent.config.yaml` file in the repository as a reference and update the paths according to your local installations of the MCP servers.

## Usage

1. Create or modify `input.json` with your configuration:
```json
{
    "root_path": "/path/to/resume/directory",
    "resume_path": "current_resume.pdf",
    "github_repos": [
        "https://github.com/username/repo1",
        "https://github.com/username/repo2"
    ],
    "job_posting_url": "https://example.com/job-posting",
    "job_description_path": "job_description.txt",
    "output_path": "tailored_resume",
    "additional_info": "additional_info.txt"
}
```

2. Run the script with the config flag:
```bash
poetry run python resume_updater.py --config input.json
```

### Configuration Parameters

- **root_path**: Base directory where your resume files are stored
- **resume_path**: Path to your current resume in PDF format (relative to root_path)
- **github_repos**: List of GitHub repository URLs that showcase relevant work
- **job_posting_url**: URL of the job posting to analyze
- **job_description_path**: Path to a text file containing additional job description details (relative to root_path)
- **output_path**: Base name for output files (will create both .md and .pdf, relative to root_path)
- **additional_info**: Optional path to a text file containing additional information to incorporate (relative to root_path)

The script will:
1. Generate a markdown file at `{root_path}/{output_path}.md`
2. Pause for your review and modifications
3. Create the final PDF at `{root_path}/{output_path}.pdf` using markdown2pdf-mcp server