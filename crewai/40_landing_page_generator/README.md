# Agent 40 - Landing Page Generator (CrewAI)

## What it does
Describe a product idea. A product analyst defines the audience and value, a copywriter writes the page copy, and a front-end developer builds a complete single-file HTML page, saved to `output/index.html`. Open it in your browser.

## Concepts you learn
- **From idea to artifact:** a crew that ends in a real file, not just text.
- **Extracting the useful part:** models often wrap code in explanations or code fences. A regular expression keeps only `<!DOCTYPE html> ... </html>`, and the run fails clearly if no full page was produced.
- **Choosing models per agent:** the developer was first given the 30B coder model. CrewAI talks to Ollama through its OpenAI-compatible endpoint, which cannot limit the context size, so that model loaded with a 262k-token context, spilled to the CPU and blocked Ollama. The 7B model is used instead (see CLAUDE.md).

## The crew
```
Product Analyst -> Conversion Copywriter -> Front-end Developer -> output/index.html
```

## Run
```
cd 50-agents-for-all
.venv-crewai\Scripts\python.exe crewai\40_landing_page_generator\main.py "an app that reminds you to water your plants"
```
Empty idea exits with code 1; if no complete HTML page is returned it prints the raw output and exits with code 2.

## Things to try
- Ask for a specific style ("dark theme", "playful") in the developer's task.
- Add a reviewer agent that checks the HTML for accessibility (alt text, headings).

## Known limits
- Simple pages only; no images or JavaScript.
- Always look at the page before using it anywhere.
