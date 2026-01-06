"use client";

import { useState, useRef, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Bot, Send, User, Sparkles, TrendingUp, AlertTriangle, Loader2 } from "lucide-react";
import { PageTransition } from "@/components/layout/PageTransition";
import { cn } from "@/lib/utils";

interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
    timestamp: Date;
    suggestions?: string[];
}

const EXAMPLE_QUERIES = [
    "Why did yield drop 5% last Tuesday?",
    "Which tool has the highest defect rate?",
    "Show me scratch defects from TOOL-3",
    "What's the trend for edge-ring defects?",
    "Compare yield between day and night shifts"
];

export default function CopilotPage() {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: "welcome",
            role: "assistant",
            content: "👋 Hi! I'm your AI Copilot for fab analytics. Ask me anything about your wafer defect data, trends, or equipment performance. Try one of the suggestions below!",
            timestamp: new Date(),
            suggestions: EXAMPLE_QUERIES.slice(0, 3)
        }
    ]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: "user",
            content: input,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);

        try {
            const response = await fetch("http://localhost:8000/api/copilot/query", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: input })
            });

            const data = await response.json();

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content: data.response || "I couldn't process that query. Please try rephrasing.",
                timestamp: new Date(),
                suggestions: data.suggestions
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            setMessages(prev => [...prev, {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content: "⚠️ Sorry, I encountered an error connecting to the analytics backend. Please make sure the server is running.",
                timestamp: new Date()
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSuggestionClick = (suggestion: string) => {
        setInput(suggestion);
    };

    return (
        <PageTransition className="flex-1 overflow-hidden">
            <div className="ml-64 h-screen flex flex-col overflow-hidden">
                {/* Header */}
                <div className="border-b p-6 shrink-0">
                    <div className="flex items-center gap-3">
                        <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-purple-500 to-cyan-500 flex items-center justify-center">
                            <Sparkles className="h-6 w-6 text-white" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold">AI Copilot</h1>
                            <p className="text-muted-foreground">Ask questions about your fab data in natural language</p>
                        </div>
                        <Badge variant="outline" className="ml-auto">
                            <span className="h-2 w-2 rounded-full bg-green-500 mr-2 animate-pulse" />
                            Online
                        </Badge>
                    </div>
                </div>

                {/* Chat Area - Now properly scrollable */}
                <div className="flex-1 overflow-y-auto p-6" ref={scrollRef}>
                    <div className="max-w-3xl mx-auto space-y-6">
                        {messages.map((message) => (
                            <div key={message.id} className={cn(
                                "flex gap-4",
                                message.role === "user" && "flex-row-reverse"
                            )}>
                                <div className={cn(
                                    "h-10 w-10 rounded-full flex items-center justify-center shrink-0",
                                    message.role === "assistant"
                                        ? "bg-gradient-to-br from-purple-500 to-cyan-500"
                                        : "bg-primary"
                                )}>
                                    {message.role === "assistant" ? (
                                        <Bot className="h-5 w-5 text-white" />
                                    ) : (
                                        <User className="h-5 w-5 text-primary-foreground" />
                                    )}
                                </div>
                                <div className={cn(
                                    "flex-1 space-y-2",
                                    message.role === "user" && "text-right"
                                )}>
                                    <div className={cn(
                                        "inline-block p-4 rounded-2xl max-w-[85%]",
                                        message.role === "assistant"
                                            ? "bg-muted text-left"
                                            : "bg-primary text-primary-foreground"
                                    )}>
                                        <p className="whitespace-pre-wrap">{message.content}</p>
                                    </div>
                                    {message.suggestions && message.suggestions.length > 0 && (
                                        <div className="flex flex-wrap gap-2 mt-2">
                                            {message.suggestions.map((suggestion, idx) => (
                                                <Button
                                                    key={idx}
                                                    variant="outline"
                                                    size="sm"
                                                    onClick={() => handleSuggestionClick(suggestion)}
                                                    className="text-xs"
                                                >
                                                    {suggestion}
                                                </Button>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}

                        {isLoading && (
                            <div className="flex gap-4">
                                <div className="h-10 w-10 rounded-full bg-gradient-to-br from-purple-500 to-cyan-500 flex items-center justify-center">
                                    <Bot className="h-5 w-5 text-white" />
                                </div>
                                <div className="bg-muted p-4 rounded-2xl">
                                    <Loader2 className="h-5 w-5 animate-spin" />
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Input Area */}
                <div className="border-t p-6 shrink-0">
                    <div className="max-w-3xl mx-auto">
                        <div className="flex gap-4">
                            <Input
                                placeholder="Ask me anything about your wafer data..."
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                                className="flex-1"
                                disabled={isLoading}
                            />
                            <Button onClick={handleSend} disabled={isLoading || !input.trim()}>
                                <Send className="h-4 w-4" />
                            </Button>
                        </div>
                        <div className="flex flex-wrap gap-2 mt-4">
                            {EXAMPLE_QUERIES.map((query, idx) => (
                                <Badge
                                    key={idx}
                                    variant="secondary"
                                    className="cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors"
                                    onClick={() => handleSuggestionClick(query)}
                                >
                                    {query}
                                </Badge>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </PageTransition>
    );
}
