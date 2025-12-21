"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from "recharts";
import { Thermometer, Gauge, Timer, Wind, Zap } from "lucide-react";
import { AppSidebar } from "@/components/layout/AppSidebar";
import { cn } from "@/lib/utils";

interface ParameterData {
    parameter: string;
    value: number;
    defect_rate: number;
    tool_id: string;
}

interface CorrelationResult {
    parameter: string;
    correlation: number;
    trend: "positive" | "negative" | "neutral";
    significance: "high" | "medium" | "low";
}

export default function ProcessParametersPage() {
    const [parameterData, setParameterData] = useState<ParameterData[]>([]);
    const [correlations, setCorrelations] = useState<CorrelationResult[]>([]);
    const [selectedParam, setSelectedParam] = useState<string>("temperature");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        generateMockData();
    }, [selectedParam]);

    const generateMockData = () => {
        // Generate realistic mock data for demo
        setLoading(true);

        const tools = ["TOOL-1", "TOOL-2", "TOOL-3", "TOOL-4", "TOOL-5"];
        const data: ParameterData[] = [];

        // Generate 50 data points
        for (let i = 0; i < 50; i++) {
            let value: number;
            let defectRate: number;

            switch (selectedParam) {
                case "temperature":
                    value = 350 + Math.random() * 50; // 350-400°C
                    defectRate = 5 + (value - 370) * 0.3 + Math.random() * 5;
                    break;
                case "pressure":
                    value = 10 + Math.random() * 20; // 10-30 mTorr
                    defectRate = 5 + Math.abs(20 - value) * 0.5 + Math.random() * 5;
                    break;
                case "time":
                    value = 30 + Math.random() * 60; // 30-90 seconds
                    defectRate = 5 + (value - 60) * 0.1 + Math.random() * 5;
                    break;
                case "gas_flow":
                    value = 100 + Math.random() * 100; // 100-200 sccm
                    defectRate = 5 + Math.abs(150 - value) * 0.1 + Math.random() * 5;
                    break;
                case "rf_power":
                    value = 200 + Math.random() * 300; // 200-500 W
                    defectRate = 5 + (value - 300) * 0.02 + Math.random() * 5;
                    break;
                default:
                    value = Math.random() * 100;
                    defectRate = Math.random() * 20;
            }

            data.push({
                parameter: selectedParam,
                value: Math.round(value * 10) / 10,
                defect_rate: Math.max(0, Math.min(30, Math.round(defectRate * 10) / 10)),
                tool_id: tools[Math.floor(Math.random() * tools.length)]
            });
        }

        setParameterData(data);

        // Generate correlations
        setCorrelations([
            { parameter: "Temperature", correlation: 0.72, trend: "positive", significance: "high" },
            { parameter: "Pressure", correlation: -0.45, trend: "negative", significance: "medium" },
            { parameter: "Process Time", correlation: 0.28, trend: "positive", significance: "low" },
            { parameter: "Gas Flow", correlation: 0.65, trend: "positive", significance: "high" },
            { parameter: "RF Power", correlation: 0.38, trend: "positive", significance: "medium" }
        ]);

        setLoading(false);
    };

    const getParamIcon = (param: string) => {
        switch (param) {
            case "temperature": return <Thermometer className="h-5 w-5" />;
            case "pressure": return <Gauge className="h-5 w-5" />;
            case "time": return <Timer className="h-5 w-5" />;
            case "gas_flow": return <Wind className="h-5 w-5" />;
            case "rf_power": return <Zap className="h-5 w-5" />;
            default: return <Gauge className="h-5 w-5" />;
        }
    };

    const getParamUnit = (param: string) => {
        switch (param) {
            case "temperature": return "°C";
            case "pressure": return "mTorr";
            case "time": return "sec";
            case "gas_flow": return "sccm";
            case "rf_power": return "W";
            default: return "";
        }
    };

    const getCorrelationColor = (corr: number) => {
        const abs = Math.abs(corr);
        if (abs > 0.6) return "text-red-500";
        if (abs > 0.3) return "text-yellow-500";
        return "text-green-500";
    };

    const CustomTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload as ParameterData;
            return (
                <div className="bg-background border rounded-lg p-3 shadow-lg">
                    <p className="font-semibold">{data.tool_id}</p>
                    <p className="text-sm">{selectedParam}: <span className="font-mono">{data.value} {getParamUnit(selectedParam)}</span></p>
                    <p className="text-sm">Defect Rate: <span className="font-mono text-destructive">{data.defect_rate}%</span></p>
                </div>
            );
        }
        return null;
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="h-12 w-12 rounded-full border-4 border-primary border-t-transparent animate-spin" />
            </div>
        );
    }

    return (
        <>
            <AppSidebar showBackButton={true} currentPage="config" />
            <div className={cn("transition-all duration-300", "ml-64")}>
                <div className="container mx-auto p-8">
                    {/* Header */}
                    <div className="mb-8 flex items-center justify-between">
                        <div>
                            <h1 className="text-4xl font-bold mb-2">Process Parameter Analytics</h1>
                            <p className="text-muted-foreground">Correlate recipe parameters with defect rates</p>
                        </div>
                        <Select value={selectedParam} onValueChange={setSelectedParam}>
                            <SelectTrigger className="w-48">
                                <SelectValue placeholder="Select Parameter" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="temperature">Temperature</SelectItem>
                                <SelectItem value="pressure">Pressure</SelectItem>
                                <SelectItem value="time">Process Time</SelectItem>
                                <SelectItem value="gas_flow">Gas Flow</SelectItem>
                                <SelectItem value="rf_power">RF Power</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>

                    {/* Correlation Summary */}
                    <div className="grid md:grid-cols-5 gap-4 mb-8">
                        {correlations.map((corr) => (
                            <Card key={corr.parameter} className={cn(
                                "cursor-pointer transition-all hover:scale-105",
                                corr.parameter.toLowerCase().replace(" ", "_") === selectedParam && "ring-2 ring-primary"
                            )}>
                                <CardHeader className="pb-2">
                                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                                        {getParamIcon(corr.parameter.toLowerCase().replace(" ", "_"))}
                                        {corr.parameter}
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className={cn("text-2xl font-bold", getCorrelationColor(corr.correlation))}>
                                        {corr.correlation > 0 ? "+" : ""}{corr.correlation.toFixed(2)}
                                    </div>
                                    <p className="text-xs text-muted-foreground capitalize">
                                        {corr.significance} significance
                                    </p>
                                </CardContent>
                            </Card>
                        ))}
                    </div>

                    {/* Scatter Plot */}
                    <Card className="mb-8">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                {getParamIcon(selectedParam)}
                                {selectedParam.charAt(0).toUpperCase() + selectedParam.slice(1).replace("_", " ")} vs Defect Rate
                            </CardTitle>
                            <CardDescription>
                                Each point represents a process run. Color indicates tool ID.
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <ResponsiveContainer width="100%" height={400}>
                                <ScatterChart>
                                    <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                                    <XAxis
                                        type="number"
                                        dataKey="value"
                                        name={selectedParam}
                                        unit={getParamUnit(selectedParam)}
                                        tick={{ fontSize: 12 }}
                                    />
                                    <YAxis
                                        type="number"
                                        dataKey="defect_rate"
                                        name="Defect Rate"
                                        unit="%"
                                        tick={{ fontSize: 12 }}
                                    />
                                    <Tooltip content={<CustomTooltip />} />
                                    <Legend />
                                    <Scatter name="Process Runs" data={parameterData} fill="#00d4ff">
                                        {parameterData.map((entry, index) => {
                                            const colors: Record<string, string> = {
                                                "TOOL-1": "#00d4ff",
                                                "TOOL-2": "#ff0055",
                                                "TOOL-3": "#22c55e",
                                                "TOOL-4": "#eab308",
                                                "TOOL-5": "#8b5cf6"
                                            };
                                            return <Cell key={index} fill={colors[entry.tool_id] || "#888"} />;
                                        })}
                                    </Scatter>
                                </ScatterChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>

                    {/* Insights */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Parameter Insights</CardTitle>
                            <CardDescription>AI-generated recommendations based on correlation analysis</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                <div className="p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                                    <p className="font-semibold text-yellow-500">⚠️ Temperature Correlation Detected</p>
                                    <p className="text-sm text-muted-foreground mt-1">
                                        Strong positive correlation (r=0.72) between temperature and defect rate.
                                        Consider tightening temperature control limits from ±10°C to ±5°C.
                                    </p>
                                </div>
                                <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                                    <p className="font-semibold text-blue-500">💡 Optimal Parameter Range</p>
                                    <p className="text-sm text-muted-foreground mt-1">
                                        Lowest defect rates observed at: Temperature 360-370°C, Pressure 18-22 mTorr,
                                        Gas Flow 140-160 sccm.
                                    </p>
                                </div>
                                <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
                                    <p className="font-semibold text-green-500">✅ Recommended Action</p>
                                    <p className="text-sm text-muted-foreground mt-1">
                                        Update recipe RECIPE-001 to use optimized parameters. Estimated yield improvement: 3-5%.
                                    </p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </>
    );
}
