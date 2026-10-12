# Agent 15 - Web Search Agent (AutoGen)

## What it does
Answers a question from the web: it searches, opens the most relevant pages, reads them, and answers in under 150 words with a Sources list.

## Concepts you learn
- **Two cooperating tools:** `web_search` finds candidate pages; `read_page` downloads a page and strips HTML down to visible text. Snippets alone are often too thin to answer accurately.
- **max_tool_iterations=4:** lets one agent run several tool rounds (search, read, maybe search again) before answering. The default is a single round.
- **Simple HTML-to-text:** regular expressions remove scripts, styles, navigation and tags, and the text is cut to 3000 characters to fit the context window.
- **Compare with Agent 01:** same goal, different framework, and this one reads full pages.

## The flow
```
question -> web_search (x1-2) -> read_page (best 1-2 URLs) -> answer + sources
```

## Run
```
cd 50-agents-for-all
.venv-autogen\Scripts\python.exe autogen\15_web_search_agent\main.py "What is the James Webb Space Telescope's primary mirror made of?"
```
Empty question exits with code 1.

## Things to try
- Ask something that needs reading a page, not just snippets ("What are the opening hours of the British Museum on Fridays?").
- Lower `max_tool_iterations` to 1 and compare.

## Known limits
- Some sites block automated downloads or need JavaScript; `read_page` then returns little text.
- In a test the model answered from search snippets and skipped `read_page`; the answer was still correct and sourced.
