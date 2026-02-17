---
title: "/skills.md: The New Interface for AI Agents"
subtitle: "How websites are discovering a better way to communicate their capabilities to AI agents"
date: "2026-02-17"
author: "Research Analysis"
tags: ["AI Agents", "Web Standards", "Agent Skills", "Future of Web", "augmi"]
---

# /skills.md: The New Interface for AI Agents

*How websites are discovering a better way to communicate their capabilities to AI agents—and why it matters for the future of the web*

---

## The Problem: Agents Without Context

When you visit a new website, you instantly understand what it does. You see the layout, read the copy, and intuitively grasp how to navigate it. But when an AI agent visits that same website, it's like a visitor from another dimension—surrounded by information but lacking the context to use it effectively.

Traditional APIs help agents retrieve data, but they don't tell agents *how* to accomplish tasks. An API might let you fetch a list of products, but it won't tell you the best workflow for placing an order, handling out-of-stock items, or applying promotional codes. This gap between data access and task completion is where agents struggle most.

The result? Capable AI systems that still can't reliably perform real work because they lack the procedural knowledge that humans take for granted.

---

## The Solution: Declaring Capabilities with /skills.md

Enter the `/skills.md` pattern—an emerging convention where websites expose a machine-readable manifest of their capabilities at a predictable URL endpoint. Think of it as `robots.txt` for the AI age, but instead of telling crawlers what *not* to index, it tells agents what they *can* do.

```
https://example.com/skills.md
```

At its core, this pattern answers a simple question: **"What can an AI agent accomplish on this website?"**

### The Analogy: From Search to Action

| File | Era | Audience | Purpose |
|------|-----|----------|---------|
| `robots.txt` | Web 1.0 | Search engines | "Here's what you can index" |
| `sitemap.xml` | Web 2.0 | Search engines | "Here's what's available" |
| `/skills.md` | Agentic Web | AI agents | "Here's what you can DO" |

While `robots.txt` and `sitemap.xml` help search engines understand *content*, `/skills.md` helps agents understand *capabilities*. It's a fundamental shift from information discovery to action enablement.

---

## Case Study: augmi.world/skills

One of the most compelling implementations of this pattern is [augmi.world/skills](https://augmi.world/skills), a skills library that demonstrates how the `/skills` endpoint can transform agent-website interaction.

### What augmi.world/skills Provides

The platform hosts 1,700+ community-built skills organized by category:

- **Content Creation**: Deep research pipelines, viral tweet crafters, spec interview tools
- **Image & Visual Generation**: Blog image generators, infographic creators
- **Video & Audio**: AI film makers, transcript extractors, music downloaders
- **Document Processing**: PDF toolkits, large document readers
- **Developer Tools**: Codebase tutors, voice-based learning systems

### Inside the Repository

The [kon-rad/augmi-skills](https://github.com/kon-rad/augmi-skills) GitHub repository reveals the actual implementation. Each skill follows the [Agent Skills](https://agentskills.io) open standard—originally developed by Anthropic.

Here's a real example from the repository—the `deep-research` skill:

```yaml
---
name: deep-research
description: Deep research workflow that takes a topic and links, conducts comprehensive research across web and social media, creates executive summaries, finds patterns and connections, then produces analysis documents, Twitter threads, blog posts, and YouTube scripts. Use this skill when the user wants to deeply research a topic, analyze multiple sources, and create multi-format content from the research.
---

# Deep Research Skill

A comprehensive research-to-content workflow that transforms a topic and source links into deep analysis and multi-platform content.

## Overview

This skill:
1. Takes a topic and optional seed links as input
2. Conducts deep research using web search, social media (Twitter/X), and other platforms
3. Scrapes and saves all research to organized folders
4. Creates one-paragraph executive summaries for each source
5. Analyzes patterns, finds deep connections across all materials
6. Produces a comprehensive analysis document with insights and conclusions
7. Transforms the analysis into Twitter threads, blog posts, and YouTube scripts
```

Notice how the skill doesn't just declare *what* it can do—it explains *how* to do it, with step-by-step instructions that an agent can follow.

---

## The Anatomy of a SKILL.md File

### Directory Structure

```
deep-research/
├── SKILL.md              # Main entry point (required)
├── template.md           # Template for outputs
├── examples/
│   └── sample-output.md  # Example results
└── scripts/
    └── research.py       # Executable helpers
```

### YAML Frontmatter

Every SKILL.md begins with structured metadata:

```yaml
---
name: blog-visual-gen
description: >
  Generates graphic visuals from blog post content using Google's 
  Nano Banana 3 model. Use this skill when users want to create 
  a visual representation of a blog post, article, or text content.
disable-model-invocation: false
user-invocable: true
allowed-tools: Read, Bash, Bash(python *)
---
```

Key fields include:

| Field | Purpose |
|-------|---------|
| `name` | Unique identifier for the skill |
| `description` | Natural language description for agent discovery |
| `disable-model-invocation` | Prevent automatic triggering |
| `user-invocable` | Allow manual /command invocation |
| `allowed-tools` | Restrict available tools for security |
| `context: fork` | Run in isolated subagent |

### Markdown Instructions

After the frontmatter comes the actual instructions—written in natural language that both humans and agents can understand:

```markdown
## How It Works

1. **Content Analysis**: The script reads the blog post and uses 
   Gemini to analyze the main theme, key concepts, emotional tone, 
   and visual metaphors present in the text.

2. **Prompt Generation**: Based on analysis, generates an optimized 
   image prompt that captures the core visual concept.

3. **Image Generation**: Uses Nano Banana 3 to create the final visual.
```

This is the genius of the pattern: **skills are just well-structured documentation** that agents can read and execute.

---

## How Agents Discover and Use Skills

### Automatic Invocation

Agents can automatically load skills when the description matches the user's intent. If a user says "create a visual for this blog post," the agent recognizes that the `blog-visual-gen` skill's description matches and loads it automatically.

### Manual Invocation

Users can also invoke skills directly using slash commands:

```
/deep-research:full topic: "AI Agents" links: [url1, url2, url3]
/blog-visual-gen:generate OUTPUT/my-post/blog-post.md
/ai-film-maker:create concept: "A day in the life of an AI"
```

### Argument Passing

Skills accept arguments through string substitution:

```yaml
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
---

Fix GitHub issue $ARGUMENTS following our coding standards.
```

---

## Skills vs. APIs: Understanding the Difference

| Aspect | APIs | Skills |
|--------|------|--------|
| **What they provide** | Data access | Task completion |
| **Interface** | Structured endpoints | Natural language instructions |
| **Flexibility** | Rigid schemas | Adaptive workflows |
| **Discovery** | Documentation sites | Descriptions agents can match |
| **Execution** | HTTP requests | Agent-driven workflows |

Skills and APIs work together. A skill might use an API internally, but the skill adds the *how*—the workflow, error handling, and best practices that raw APIs don't provide.

---

## The Ecosystem: Beyond augmi.world

### ClawHub (clawhub.ai)
OpenClaw's public skills registry hosts 3,000+ community-built skills with security scanning via VirusTotal partnership.

### VoltAgent Awesome List
The [awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills) repository curates 3,002+ skills with quality filtering.

### Claude Code
Anthropic's Claude Code implements the full Agent Skills specification with multi-level skill storage and nested directory discovery.

---

## The Future: Toward an Agentic Web

### Standard Discovery Protocols

Imagine a world where every website exposes its capabilities through well-known endpoints:

```
https://shop.example.com/.well-known/agent-skills
https://bank.example.com/skills.md
https://gov.example.com/ai-capabilities
```

### The Vision

The ultimate vision is a web where:
- **Every website declares its agent capabilities**
- **Agents discover and use capabilities dynamically**
- **Users accomplish complex tasks through natural language**
- **The barrier between human and machine interaction disappears**

---

## Implementation Guide

### Step 1: Create Your Skills Directory

```
your-website/
├── public/
│   └── skills/
│       ├── SKILL.md          # Main manifest
│       ├── search/
│       │   └── SKILL.md      # Search capability
│       └── order/
│           └── SKILL.md      # Order placement
```

### Step 2: Write Your Main Manifest

```yaml
---
name: example-shop
description: An e-commerce website with search, ordering, and support capabilities.
version: 1.0.0
---

# Example Shop Skills

## Available Capabilities

### Product Search (`/search`)
Find products by name, category, price range, or attributes.

### Order Placement (`/order`)
Place orders with shipping options and payment processing.
```

### Step 3: Expose at /skills.md

```javascript
// Express.js example
app.get('/skills.md', (req, res) => {
  res.sendFile(path.join(__dirname, 'public/skills/SKILL.md'));
});
```

---

## Conclusion: The Interface Revolution

The `/skills.md` pattern represents more than a technical convention—it signals a fundamental shift in how we think about web interfaces.

For decades, we've built interfaces for humans: graphical designs, navigation menus, forms, and buttons. The `/skills.md` pattern acknowledges that **agents are becoming first-class users of the web**, and they need interfaces too—not graphical ones, but capability manifests written in natural language.

The implications are profound. When every website can declare its capabilities in a machine-readable format, we move from:
- **Information retrieval** to **task completion**
- **Screen scraping** to **capability negotiation**
- **Human-driven workflows** to **agent-orchestrated processes**

The web was built for humans. Now it's learning to speak agent.

---

## Resources

- [Agent Skills Specification](https://agentskills.io)
- [augmi.world/skills](https://augmi.world/skills)
- [kon-rad/augmi-skills](https://github.com/kon-rad/augmi-skills)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills)