# Advanced RAG Assignment: Code Q&A and Multi-Source Retrieval

> **Note:** This is a challenging assignment - start early! The goal is learning through exploration, not perfection. You will encounter problems that require experimentation and iteration. Embrace the difficulty - this is how real-world RAG systems are built. Ask questions, try different approaches, and document what you learn along the way.

This assignment builds on the concepts from the Basic RAG Lab. You will implement two advanced RAG systems that introduce routing, tool use, and multi-source retrieval - key concepts that bridge basic RAG to agentic RAG patterns.

## Learning Objectives

- Build RAG systems that work with code and multiple file types
- Implement query routing to select appropriate retrieval strategies
- Combine keyword search (grep/BM25) with semantic search
- Handle structured and unstructured data sources
- Introduce tool-use patterns (without full agent frameworks)

## Prerequisites

- Completed the Basic RAG Lab
- Understanding of chunking, indexing, and retrieval strategies
- Familiarity with vector stores and embeddings
- Python 3.10+
- API keys (Groq is FREE)

## Assignment Overview

This assignment has two parts:

### Part 1: Code Q&A System with Bash Tools (100 points)

Build a RAG system that can answer questions about the `mcp-gateway-registry` codebase using bash tools for context retrieval.

**The Codebase:**

Clone the target codebase into your project directory:

```bash
git clone https://github.com/agentic-community/mcp-gateway-registry
```

The `mcp-gateway-registry` repository is a real open-source project - an MCP (Model Context Protocol) gateway and registry system. It includes:
- Python backend (FastAPI)
- TypeScript/React CLI and frontend
- Authentication and authorization systems
- Database integrations (MongoDB)
- Docker and Kubernetes deployment configs
- Extensive documentation

**System Architecture:**

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌─────────────┐
│ User Query  │────>│  Query Router    │────>│  Bash Tool(s)   │────>│ LLM Answer  │
│             │     │ (classify query) │     │  Execute & Get  │     │ with Context│
└─────────────┘     └──────────────────┘     │  File Contents  │     └─────────────┘
                                             └─────────────────┘
```

**The Approach:**

Instead of traditional vector-based retrieval, you will use bash tools (grep, find, cat, tree, etc.) to retrieve relevant context from the codebase. This introduces tool-use patterns that bridge basic RAG to agentic RAG.

Your system should:
1. **Classify** the incoming question to determine what type of information is needed
2. **Select** the appropriate bash tool(s) to retrieve relevant context
3. **Execute** the bash commands and collect the output
4. **Pass** the retrieved context along with the question to an LLM
5. **Generate** an answer with references to specific files

**Bash Tools to Consider:**
- `grep` / `rg` (ripgrep) - Search file contents for patterns
- `find` - Locate files by name or pattern
- `cat` / `head` / `tail` - Read file contents
- `tree` - Visualize directory structure
- `ls` - List directory contents

**Test Questions:**

Your system should be able to answer the following questions:

| # | Question | Difficulty |
|---|----------|------------|
| 1 | "What Python dependencies does this project use?" | Simple |
| 2 | "What is the main entry point file for the registry service?" | Simple |
| 3 | "What programming languages and file types are used in this repository? (e.g., Python, TypeScript, YAML, JSON, Dockerfile, etc.)" | Simple |
| 4 | "How does the authentication flow work, from token validation to user authorization?" | Difficult |
| 5 | "What are all the API endpoints available in the registry service and what scopes do they require?" | Difficult |
| 6 | "How would you add support for a new OAuth provider (e.g., Okta) to the authentication system? What files would need to be modified and what interfaces must be implemented?" | Very Hard |

*Note: Questions 4-6 require synthesizing information from multiple files (code + docs + configs).*

**Hints:**
- Different question types need different retrieval strategies
- Structure questions might use `tree` or `find`
- Code search questions might use `grep` with file type filters
- Dependency questions should look at `pyproject.toml` and `package.json`
- Documentation questions should search the `docs/` folder

### Part 2: Multi-Source RAG with Routing (100 points)

Build a RAG system that intelligently routes queries to different data sources based on the question type.

**The Data:**

The `data/` folder contains two types of data sources simulating an e-commerce analytics scenario:

```
data/
├── structured/
│   └── daily_sales.csv      # 1000 rows of sales transactions
└── unstructured/
    ├── ELEC001_product_page.txt   # Product descriptions & reviews
    ├── HOME003_product_page.txt
    ├── SPRT001_product_page.txt
    ├── BEAU001_product_page.txt
    ├── CLTH001_product_page.txt
    ├── BOOK001_product_page.txt
    ├── TOYS001_product_page.txt
    ├── OFFC001_product_page.txt
    ├── PETS001_product_page.txt
    └── FOOD001_product_page.txt
```

**Structured Data (CSV):**
- 1000 daily sales records across 90 days (Oct-Dec 2024)
- 35 products across 10 categories
- Columns: `date, product_id, product_name, category, units_sold, unit_price, total_revenue, region`
- Regions: North, South, East, West, Central

**Unstructured Data (Text):**
- 10 product pages with detailed descriptions, specifications, and customer reviews
- Similar to what you'd find on an e-commerce website
- Includes product features, technical specs, and 5 customer reviews per product

**System Architecture:**

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌─────────────┐
│ User Query  │────>│  Query Router    │────>│  Data Source(s) │────>│ LLM Answer  │
│             │     │ (classify query) │     │  CSV | Text     │     │ with Context│
└─────────────┘     └──────────────────┘     └─────────────────┘     └─────────────┘
                            │
                            ├── Analytical/numerical → CSV (use bash: grep, awk, cut)
                            ├── Product details/reviews → Unstructured text
                            └── Both → Combine sources
```

**Test Questions:**

Your system should be able to answer the following questions:

| # | Question | Source Required |
|---|----------|-----------------|
| 1 | "What was the total revenue for Electronics category in December 2024?" | CSV Only |
| 2 | "Which region had the highest sales volume?" | CSV Only |
| 3 | "What are the key features of the Wireless Bluetooth Headphones?" | Text Only |
| 4 | "What do customers say about the Air Fryer's ease of cleaning?" | Text Only |
| 5 | "Which product has the best customer reviews and how well is it selling?" | Both (Text + CSV) |
| 6 | "I want a product for fitness that is highly rated and sells well in the West region. What do you recommend?" | Both (Text + CSV) |

*Note: Questions 1-2 require filtering/aggregating CSV data. Questions 3-4 require searching unstructured text. Questions 5-6 require combining insights from both sources.*

**What you'll implement:**
- Query router that classifies questions and selects appropriate data source(s)
- CSV retrieval using bash tools (grep, awk, cut) or pandas
- Text retrieval using semantic search or keyword matching
- Result combination strategy for multi-source queries
- Answer generation with the LLM

## Getting API Keys

| Provider | Link | Notes |
|----------|------|-------|
| **Groq** (Recommended) | https://console.groq.com/ | FREE tier, no credit card |
| OpenAI | https://platform.openai.com/ | Paid |
| Anthropic | https://console.anthropic.com/ | Paid |
| Cohere | https://dashboard.cohere.com/ | FREE tier (for re-ranking) |

## Environment Setup

### Step 1: Install uv (Python Package Manager)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart your shell or run:
source $HOME/.local/bin/env
```

### Step 2: Create Virtual Environment and Install Dependencies

```bash
# Navigate to the assignment directory
cd <your-repo-path>

# Create virtual environment and install all dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Register the Kernel for Jupyter

```bash
# Register the kernel (run this with venv activated)
uv run python -m ipykernel install --user --name=advanced-rag --display-name="Advanced RAG"
```

### Step 4: Configure Your API Keys

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API key(s)
```

## Project Structure

```
advanced-rag/
├── mcp-gateway-registry/  # Target codebase for Part 1 (clone from GitHub)
│   ├── registry/          # Python FastAPI backend
│   ├── cli/               # TypeScript CLI application
│   ├── frontend/          # React frontend
│   ├── auth_server/       # Authentication service
│   ├── docs/              # Project documentation
│   └── ...
├── data/                  # Data sources for Part 2
│   ├── structured/
│   │   └── daily_sales.csv       # 1000 sales records
│   └── unstructured/
│       └── *_product_page.txt    # 10 product descriptions & reviews
├── scripts/
│   └── generate_data.py   # Script to regenerate data
├── notebooks/
│   ├── part1_code_qa.ipynb
│   └── part2_multi_source.ipynb
├── src/                   # Your implementation
├── tests/                 # Test cases
├── .env.example
├── pyproject.toml
└── README.md
```

## Key Concepts

### Query Routing

Instead of always using the same retrieval strategy, a router decides:
- Which data source(s) to query
- Which retrieval method to use (semantic, keyword, hybrid)
- Whether to rewrite the query for specific sources

```
User Query -> Router -> [Source A, Source B] -> Combine Results -> Generate Answer
```

### Code-Aware Chunking

Standard text splitters don't understand code structure. For code:
- Split by functions/classes, not arbitrary character counts
- Preserve imports and context
- Handle different languages/file types appropriately

### Hybrid Retrieval

Combine multiple retrieval strategies:
- **Semantic Search**: Good for conceptual questions ("How does X work?")
- **Keyword Search**: Good for specific terms, function names, error messages
- **Ensemble**: Weight and combine results from both

## Deliverables

### Part 1: Code Q&A with Bash Tools (100 points)
- [x] Implement query classification to determine question type
- [x] Implement bash tool selection logic based on query type
- [x] Execute bash commands and capture output as context
- [x] Pass context to LLM and generate answers
- [x] Answer test questions correctly with file references
- [x] Save results to `part1_results.txt`

### Part 2: Multi-Source RAG (100 points)
- [x] Implement query router
- [x] Handle at least 3 different source types
- [x] Implement source-specific retrieval
- [x] Combine results from multiple sources
- [x] Save results to `part2_results.txt`

## Grading Criteria

| Criteria | Points |
|----------|--------|
| Part 1: Query classification logic | 20 |
| Part 1: Bash tool selection and execution | 40 |
| Part 1: Answer quality on test questions | 40 |
| Part 2: Query router implementation | 30 |
| Part 2: Multi-source handling | 30 |
| Part 2: Answer quality on test questions | 40 |
| **Total** | **200** |

## Tips

1. **Explore the codebase first** - Spend time understanding the mcp-gateway-registry structure
2. **Test bash commands manually** - Try grep, find, and cat commands in terminal before coding
3. **Use logging** - Log which bash commands are executed and what context is retrieved
4. **Handle command output size** - Bash output can be large; consider truncating or summarizing
5. **Include file references** - Good answers cite specific files and line numbers

## Resources

### Part 1: Bash Tools and Subprocess
- [Python subprocess module](https://docs.python.org/3/library/subprocess.html)
- [grep manual](https://www.gnu.org/software/grep/manual/grep.html)
- [find manual](https://www.gnu.org/software/findutils/manual/html_mono/find.html)
- [ripgrep (rg) - faster grep alternative](https://github.com/BurntSushi/ripgrep)

### Part 2: LangChain Resources
- [LangChain Routing](https://python.langchain.com/docs/how_to/routing/)
- [Ensemble Retriever](https://python.langchain.com/docs/how_to/ensemble_retriever/)
- [BM25 Retriever](https://python.langchain.com/docs/integrations/retrievers/bm25/)

## Submission

Commit and push all required files:
- Completed notebooks
- `part1_results.txt`
- `part2_results.txt`
- Any source code in `src/`
