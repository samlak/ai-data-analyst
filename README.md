# AI Procurement Data Analyst

An intelligent application that allows users to analyze procurement data using **natural language queries**. This project leverages cutting-edge **Azure OpenAI** for code generation and data analysis, enabling seamless interactions for generating insights, visualizations, and tabular reports. The system is divided into two key components:

1. **Backend**: A FastAPI server for natural language processing, Python code execution, and MongoDB data querying.
2. **Frontend**: A React-based user interface for intuitive interaction, result visualization, and chart downloads.

[![Watch the AI Procurement Data Analyst Demo](/frontend/public/demo-thumbnail.png)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

[**Watch the AI Procurement Data Analyst Demo**](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

---

## Project Structure

```plaintext
.
├── server/                  # Backend server with FastAPI
├── frontend/                # React-based frontend interface
├── README.md                # Main project README (this file)
```

---

## Implementation Overview

### Backend - FastAPI Server
The backend processes user queries and handles the core functionalities:
- Interprets natural language queries using Azure OpenAI.
- Generates and executes Python code to query MongoDB.
- Returns tabular data, visualizations, or analysis summaries to the frontend.

For more details, see the [Backend README](server/README.md).

---

### Frontend - React Interface
The frontend is a sleek and user-friendly interface:
- Allows users to type queries or choose from suggested questions.
- Displays results as tables, charts, or summaries.
- Provides options to download or preview generated images.

For more details, see the [Frontend README](frontend/README.md).



