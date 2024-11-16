import React from 'react';
import { MessageSquare } from 'lucide-react';

interface SuggestedQuestionsProps {
  onSelectQuestion: (question: string) => void;
}

const suggestedQuestions = [
  "What are the top 5 most purchased items?",
  "Show me the distribution of purchase amounts",
  "What's the average purchase amount?",
  "Which day of the week has the most purchases?",
  "What's the trend of purchases over time?",
];

export function SuggestedQuestions({ onSelectQuestion }: SuggestedQuestionsProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 text-sm text-gray-600">
        <MessageSquare className="w-4 h-4" />
        <span>Suggested questions</span>
      </div>
      <div className="grid gap-2">
        {suggestedQuestions.map((question, index) => (
          <button
            key={index}
            onClick={() => onSelectQuestion(question)}
            className="text-left px-3 py-2 text-sm text-gray-700 bg-white hover:bg-gray-50 rounded-lg border border-gray-200 transition-colors"
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
}