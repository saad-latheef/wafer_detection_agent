"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Brain, AlertTriangle, CheckCircle2, Target, TrendingUp, TrendingDown, Minus, Loader2, ChevronRight, Wrench, Shield } from "lucide-react";
import { PageTransition } from "@/components/layout/PageTransition";
import { cn } from "@/lib/utils";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, PieChart, Pie } from "recharts";

interface FiveWhyStep {
    level: number;
    question: string;
    answer: string;
}

interface CorrectiveAction {
    priority: string;
    action: string;
    owner: string;
    due: string;
    rationale?: string;
}

interface PreventiveAction {
    priority: string;
    action: string;
    owner: string;
    due: string;
    expected_impact: string;
}

interface RCAData {
    analysis_date: string;
    date_range: { start: string; end: string };
    summary: {
        total_defects: number;
        top_defect_pattern: string;
        worst_tool: string;
        worst_tool_defect_rate: number;
        trend_direction: string;
    };
    defect_distribution: Array<{ pattern: string; count: number; percentage: number }>;
    tool_analysis: Array<{ tool_id: string; total_wafers: number; defective: number; defect_rate: number }>;
    weekly_trend: Array<{ week: string; count: number }>;
    five_whys: FiveWhyStep[];
    fishbone: Record<string, string[]>;
    corrective_actions: CorrectiveAction[];
    preventive_actions: PreventiveAction[];
}

export default function RCAPage() {
    const [data, setData] = useState<RCAData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchAnalysis();
    }, []);

    const fetchAnalysis = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch("http://localhost:8000/api/root-cause-analysis");
            if (!response.ok) throw new Error("Failed to fetch analysis");
            const result = await response.json();
            setData(result);
        } catch (err) {
            setError("Failed to load analysis. Please ensure the backend is running.");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const getTrendIcon = (trend: string) => {
        switch (trend) {
            case "increasing": return <TrendingUp className="h-5 w-5 text-destructive" />;
            case "decreasing": return <TrendingDown className="h-5 w-5 text-green-500" />;
            default: return <Minus className="h-5 w-5 text-muted-foreground" />;
        }
    };

    const getPriorityColor = (priority: string) => {
        switch (priority.toLowerCase()) {
            case "critical": return "bg-red-500";
            case "high": return "bg-orange-500";
            case "medium": return "bg-yellow-500";
            case "low": return "bg-green-500";
            default: return "bg-gray-500";
        }
    };

    const COLORS = ['#00d4ff', '#ff0055', '#22c55e', '#eab308', '#8b5cf6', '#f97316'];

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen ml-64">
                <div className="text-center">
                    <Loader2 className="h-12 w-12 animate-spin mx-auto mb-4 text-primary" />
                    <p className="text-muted-foreground">Analyzing defect data...</p>
                </div>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="flex items-center justify-center min-h-screen ml-64">
                <div className="text-center">
                    <AlertTriangle className="h-12 w-12 mx-auto mb-4 text-destructive" />
                    <p className="text-destructive">{error}</p>
                </div>
            </div>
        );
    }

    return (
        <PageTransition>
            <div className={cn("transition-all duration-300", "ml-64")}>
                <div className="container mx-auto p-8">
                    {/* Header */}
                    <div className="mb-8">
                        <div className="flex items-center gap-3 mb-2">
                            <Brain className="h-8 w-8 text-primary" />
                            <h1 className="text-4xl font-bold">Root Cause Analysis</h1>
                        </div>
                        <p className="text-muted-foreground">
                            Automated analysis based on {data.summary.total_defects} defects from the last 30 days
                        </p>
                    </div>

                    {/* Summary Cards */}
                    <div className="grid md:grid-cols-4 gap-4 mb-8">
                        <Card className="border-l-4 border-l-destructive">
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm font-medium">Top Defect Pattern</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold text-destructive">{data.summary.top_defect_pattern}</div>
                                <p className="text-xs text-muted-foreground">Highest occurrence</p>
                            </CardContent>
                        </Card>
                        <Card className="border-l-4 border-l-orange-500">
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm font-medium">Problem Tool</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold text-orange-500">{data.summary.worst_tool}</div>
                                <p className="text-xs text-muted-foreground">{data.summary.worst_tool_defect_rate}% defect rate</p>
                            </CardContent>
                        </Card>
                        <Card className="border-l-4 border-l-primary">
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm font-medium">Total Defects</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{data.summary.total_defects}</div>
                                <p className="text-xs text-muted-foreground">Last 30 days</p>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm font-medium flex items-center gap-2">
                                    Trend {getTrendIcon(data.summary.trend_direction)}
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold capitalize">{data.summary.trend_direction}</div>
                                <p className="text-xs text-muted-foreground">Week over week</p>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Charts Row */}
                    <div className="grid md:grid-cols-2 gap-6 mb-8">
                        {/* Defect Distribution */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Defect Distribution</CardTitle>
                                <CardDescription>Breakdown by pattern type</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <ResponsiveContainer width="100%" height={250}>
                                    <PieChart>
                                        <Pie
                                            data={data.defect_distribution}
                                            dataKey="count"
                                            nameKey="pattern"
                                            cx="50%"
                                            cy="50%"
                                            outerRadius={80}
                                            label={({ pattern, percentage }) => `${pattern}: ${percentage}%`}
                                        >
                                            {data.defect_distribution.map((_, index) => (
                                                <Cell key={index} fill={COLORS[index % COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <Tooltip />
                                    </PieChart>
                                </ResponsiveContainer>
                            </CardContent>
                        </Card>

                        {/* Tool Performance */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Tool Defect Rates</CardTitle>
                                <CardDescription>Defect rate by equipment</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <ResponsiveContainer width="100%" height={250}>
                                    <BarChart data={data.tool_analysis}>
                                        <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                                        <XAxis dataKey="tool_id" tick={{ fontSize: 12 }} />
                                        <YAxis tickFormatter={(v) => `${v}%`} />
                                        <Tooltip formatter={(value: number) => `${value}%`} />
                                        <Bar dataKey="defect_rate" fill="#00d4ff">
                                            {data.tool_analysis.map((entry, index) => (
                                                <Cell
                                                    key={index}
                                                    fill={entry.tool_id === data.summary.worst_tool ? '#ff0055' : '#00d4ff'}
                                                />
                                            ))}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            </CardContent>
                        </Card>
                    </div>

                    {/* 5-Why Analysis */}
                    <Card className="mb-8">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Target className="h-5 w-5 text-primary" />
                                5-Why Analysis: {data.summary.top_defect_pattern} Defects on {data.summary.worst_tool}
                            </CardTitle>
                            <CardDescription>Data-driven root cause investigation</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {data.five_whys.map((step, index) => (
                                    <div key={index} className="flex gap-4">
                                        <div className="flex flex-col items-center">
                                            <div className={cn(
                                                "h-10 w-10 rounded-full flex items-center justify-center font-bold text-white",
                                                index === data.five_whys.length - 1 ? "bg-green-500" : "bg-primary"
                                            )}>
                                                {index + 1}
                                            </div>
                                            {index < data.five_whys.length - 1 && (
                                                <div className="w-0.5 h-full bg-border flex-1 my-2" />
                                            )}
                                        </div>
                                        <div className="flex-1 pb-4">
                                            <p className="font-semibold text-primary">{step.question}</p>
                                            <p className="text-muted-foreground mt-1">{step.answer}</p>
                                        </div>
                                    </div>
                                ))}

                                {data.five_whys.length > 0 && (
                                    <div className="mt-4 p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
                                        <div className="flex items-center gap-2 mb-2">
                                            <CheckCircle2 className="h-5 w-5 text-green-500" />
                                            <span className="font-bold text-green-500">Root Cause Identified</span>
                                        </div>
                                        <p className="text-lg">{data.five_whys[data.five_whys.length - 1]?.answer}</p>
                                    </div>
                                )}
                            </div>
                        </CardContent>
                    </Card>

                    {/* CAPA Section */}
                    <div className="grid md:grid-cols-2 gap-6 mb-8">
                        {/* Corrective Actions */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Wrench className="h-5 w-5 text-orange-500" />
                                    Corrective Actions
                                </CardTitle>
                                <CardDescription>Immediate actions to address the issue</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    {data.corrective_actions.map((action, index) => (
                                        <div key={index} className="border rounded-lg p-4">
                                            <div className="flex items-center gap-2 mb-2">
                                                <Badge className={getPriorityColor(action.priority)}>{action.priority}</Badge>
                                                <span className="text-sm text-muted-foreground">Due: {action.due}</span>
                                            </div>
                                            <p className="font-medium">{action.action}</p>
                                            <p className="text-sm text-muted-foreground mt-1">Owner: {action.owner}</p>
                                            {action.rationale && (
                                                <p className="text-xs text-muted-foreground mt-2 italic">{action.rationale}</p>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>

                        {/* Preventive Actions */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Shield className="h-5 w-5 text-green-500" />
                                    Preventive Actions
                                </CardTitle>
                                <CardDescription>Long-term measures to prevent recurrence</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    {data.preventive_actions.map((action, index) => (
                                        <div key={index} className="border rounded-lg p-4">
                                            <div className="flex items-center gap-2 mb-2">
                                                <Badge className={getPriorityColor(action.priority)}>{action.priority}</Badge>
                                                <span className="text-sm text-muted-foreground">Due: {action.due}</span>
                                            </div>
                                            <p className="font-medium">{action.action}</p>
                                            <p className="text-sm text-muted-foreground mt-1">Owner: {action.owner}</p>
                                            <p className="text-xs text-green-600 mt-2">
                                                <CheckCircle2 className="h-3 w-3 inline mr-1" />
                                                {action.expected_impact}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Fishbone Diagram */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Ishikawa (Fishbone) Analysis</CardTitle>
                            <CardDescription>6M factors contributing to {data.summary.top_defect_pattern} defects</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="grid md:grid-cols-3 gap-4">
                                {Object.entries(data.fishbone).map(([category, items]) => (
                                    <div key={category} className="p-4 border rounded-lg">
                                        <h4 className="font-semibold mb-3 capitalize flex items-center gap-2">
                                            {category === "man" && "👤"}
                                            {category === "machine" && "⚙️"}
                                            {category === "material" && "🧪"}
                                            {category === "method" && "📋"}
                                            {category === "measurement" && "📏"}
                                            {category === "environment" && "🌡️"}
                                            {category.charAt(0).toUpperCase() + category.slice(1)}
                                        </h4>
                                        <ul className="space-y-2">
                                            {items.map((item, i) => (
                                                <li key={i} className="text-sm flex items-start gap-2">
                                                    <ChevronRight className="h-4 w-4 shrink-0 mt-0.5 text-muted-foreground" />
                                                    {item}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </PageTransition>
    );
}
