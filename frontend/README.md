# AI Procurement Data Analyst - Frontend Guide

The **AI Procurement Data Analyst** frontend is a React-based application that allows users to interact with procurement data through natural language queries. It connects to a FastAPI backend and leverages AI to provide data insights with visualizations and tables. This guide focuses exclusively on setting up and running the **frontend**.

---

![AI Data Data Analyst](/frontend/public/demo-thumbnail.png)

---

## Prerequisites

Ensure you have the following installed:

- **Node.js 16+**
- **npm** or **yarn**

---

## Environment Variables

The frontend requires an `.env` file for configuration. Create a `.env` file in the `frontend` directory with the following:

```env
VITE_BACKEND_URL=http://localhost:8000
```

Replace `http://localhost:8000` with your FastAPI server's URL if different.

---

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/samlak/ai-data-analyst
cd ai-data-analyst/frontend
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Start the Development Server

```bash
npm run dev
```

### 4. Access the Application

Open your browser and navigate to `http://localhost:5173`.

---

## Directory Structure

```plaintext
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── ChatMessage.tsx   # Input field for natural language queries
│   │   ├── ChatMessage.tsx # Display chat messages and data analysis results
│   │   ├── ImageViewer.tsx  # Chart rendering component
│   │   └── SuggestedQuestions.tsx # Suggested questions for users
│   ├── App.tsx              # Main application component
├── index.html               # Base HTML file
└── package.json             # Dependency and project configuration
```

---

## How It Works

1. **Query Submission**:
   - Users submit a natural language question through the input field.
   - The query is sent to the backend at the `VITE_BACKEND_URL`.

2. **Data Analysis**:
   - Backend processes the query and returns analysis results.
   - Responses include data in tabular form and visualizations as image URLs.

3. **Result Display**:
   - The frontend renders tables and charts dynamically.
   - Users can download visualizations or explore data interactively.

---

## Key Components

1. **`ChatMessage`**  
   - Allows users to type and submit questions.
   - Sends queries to the backend using the `VITE_BACKEND_URL`.

2. **`ImageViewer`**  
   - Renders visualizations from backend-provided image URLs.
   - Includes download functionality for charts.

4. **`SuggestedQuestions`**  
   - Offers example questions to guide user interactions.

---

## Example Usage

### Ask Questions
- "What are the top procurement categories by spending?"
- "Show the monthly trend of IT equipment purchases."

### View Results
- Tabular data appears in a table.
- Visualizations (e.g., bar or line charts) are displayed for relevant queries.

### Download Visualizations
- Click the download button under any chart to save it as a PNG.

---

## Customization

1. **Modify Components**:
   - Add or update components in the `src/components/` directory to extend functionality.

2. **Styling**:
   - Adjust styles in `index.css` or create new stylesheets for custom designs.

3. **API URL**:
   - Update the `VITE_BACKEND_URL` in `.env` if the backend URL changes.
