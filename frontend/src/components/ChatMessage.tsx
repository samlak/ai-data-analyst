import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Bot, User } from 'lucide-react';
import { Message } from '../types';
import { ImageViewer } from './ImageViewer';

interface ChatMessageProps {
  message: Message;
}

const BACKEND_URL: string = import.meta.env.VITE_APP_BACKEND_URL || "http://localhost:8000";

function isHTMLTable(content: string): boolean {
  return content.trim().startsWith('<table') && content.trim().endsWith('</table>');
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isAssistant = message.type === 'assistant';
  const isTable = message.tableOutput && isHTMLTable(message.content);

  return (
    <div className={`flex gap-4 p-4 ${isAssistant ? 'bg-gray-50' : ''}`}>
      <div className="flex-shrink-0">
        {isAssistant ? (
          <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
        ) : (
          <div className="w-8 h-8 bg-gray-500 rounded-lg flex items-center justify-center">
            <User className="w-5 h-5 text-white" />
          </div>
        )}
      </div>
      
      <div className="flex-1 space-y-4">
        {message.loading ? (
          <div className="flex gap-1">
            <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        ) : message.error ? (
          <div className="text-red-500">
            An error occurred while processing your request. Please try again.
          </div>
        ) : (
          <div className="space-y-4">
            <div className="prose max-w-none overflow-x-auto">
              {isTable ? (
                <div 
                  className="table-wrapper"
                  dangerouslySetInnerHTML={{ __html: message.content }} 
                />
              ) : (
                <ReactMarkdown>{message.content}</ReactMarkdown>
              )}
            </div>
            
            {message.imageUrl && (
              <ImageViewer 
                src={`${BACKEND_URL}${message.imageUrl}`} 
                alt="Data visualization" 
              />
            )}
            
            {message.analysis && (
              <div className="mt-2 p-3 bg-blue-50 rounded-lg text-blue-800">
                <strong>Analysis:</strong> {message.analysis}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}