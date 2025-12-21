"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine, ReferenceArea } from "recharts";
import { AlertTriangle, CheckCircle2, Activity, TrendingDown, TrendingUp } from "lucide-react";
import { AppSidebar } from "@/components/layout/AppSidebar";
import { cn } from "@/lib/utils";

interface SPCDataPoint {
    date: string;
    total: number;
    defective: number;
    value: number;
    violations: Array<{
        rule: number;
        description: string;
        severity: string;
    }>;
    is_out_of_control: boolean;
    zone: string;
}

interface ControlLimits {
    ucl: number;
    lcl: number;
    cl: number;
    std_dev: number;
    data_points: number;
}

interface SPCSummary {
    total_points: number;
    out_of_control_count: number;
    out_of_control_rate: number;
    rule_violations: Record<number, number>;
    process_stability: "stable" | "warning" | "unstable";
}

interface SPCResponse {
    data: SPCDataPoint[];
    control_limits: ControlLimits;
    summary: SPCSummary;
    tool_id: string | null;
    date_range: {
        start: string;
        end: string;
    };
}

export default function SPCPage() {
    const [spcData, setSpcData] = useState<SPCResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [selectedTool, setSelectedTool] = useState<string>("all");
    const [days, setDays] = useState<number>(30);

    useEffect(() => {
        fetchSPCData();
    }, [selectedTool, days]);

    const fetchSPCData = async () => {
        setLoading(true);
        try {
            const toolParam = selectedTool !== "all" ? `&tool_id=${selectedTool}` : "";
            const response = await fetch(`http://localhost:8000/api/spc?days=${days}${toolParam}`);
            const data = await response.json();
            setSpcData(data);
        } catch (error) {
            console.error("Failed to fetch SPC data:", error);
        } finally {
            setLoading(false);
        }
    };

    const getStabilityColor = (stability: string) => {
        switch (stability) {
            case "stable": return "text-green-500";
            case "warning": return "text-yellow-500";
            case "unstable": return "text-red-500";
            default: return "text-muted-foreground";
        }
    };

    const getStabilityIcon = (stability: string) => {
        switch (stability) {
            case "stable": return <CheckCircle2 className="h-6 w-6 text-green-500" />;
            case "warning": return <AlertTriangle className="h-6 w-6 text-yellow-500" />;
            case "unstable": return <AlertTriangle className="h-6 w-6 text-red-500" />;
            default: return <Activity className="h-6 w-6" />;
        }
    };

    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            const point = payload[0].payload as SPCDataPoint;
            return (
                <div className="bg-background border rounded-lg p-3 shadow-lg">
                    <p className="font-semibold">{label}</p>
                    <p className="text-sm">Defect Rate: <span className="font-mono">{point.value.toFixed(2)}%</span></p>
                    <p className="text-sm text-muted-foreground">{point.defective}/{point.total} defective</p>
                    {point.violations.length > 0 && (
                        <div className="mt-2 pt-2 border-t">
                            <p className="text-sm font-semibold text-destructive">⚠️ Violations:</p>
                            {point.violations.map((v, i) => (
                                <p key={i} className="text-xs text-destructive">{v.description}</p>
                            ))}
                        </div>
                    )}
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
            <AppSidebar showBackButton={true} currentPage="spc" />
            <div className={cn("transition-all duration-300", "ml-64")}>
                <div className="container mx-auto p-8">
                    {/* Header */}
                    <div className="mb-8 flex items-center justify-between">
                        <div>
                            <h1 className="text-4xl font-bold mb-2">Statistical Process Control</h1>
                            <p className="text-muted-foreground">Real-time control charts with Western Electric Rules</p>
                        </div>
                        <div className="flex gap-4">
                            <Select value={days.toString()} onValueChange={(v) => setDays(parseInt(v))}>
                                <SelectTrigger className="w-32">
                                    <SelectValue placeholder="Time Range" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="7">7 Days</SelectItem>
                                    <SelectItem value="14">14 Days</SelectItem>
                                    <SelectItem value="30">30 Days</SelectItem>
                                    <SelectItem value="90">90 Days</SelectItem>
                                </SelectContent>
                            </Select>
                            <Select value={selectedTool} onValueChange={setSelectedTool}>
                                <SelectTrigger className="w-40">
                                    <SelectValue placeholder="All Tools" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">All Tools</SelectItem>
                                    <SelectItem value="TOOL-1">TOOL-1</SelectItem>
                                    <SelectItem value="TOOL-2">TOOL-2</SelectItem>
                                    <SelectItem value="TOOL-3">TOOL-3</SelectItem>
                                    <SelectItem value="TOOL-4">TOOL-4</SelectItem>
                                    <SelectItem value="TOOL-5">TOOL-5</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    {/* Summary Cards */}
                    {spcData && (
                        <div className="grid md:grid-cols-4 gap-4 mb-8">
                            <Card>
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                    <CardTitle className="text-sm font-medium">Process Status</CardTitle>
                                    {getStabilityIcon(spcData.summary.process_stability)}
                                </CardHeader>
                                <CardContent>
                                    <div className={cn("text-2xl font-bold capitalize", getStabilityColor(spcData.summary.process_stability))}>
                                        {spcData.summary.process_stability}
                                    </div>
                                    <p className="text-xs text-muted-foreground">
                                        Based on {spcData.summary.total_points} data points
                                    </p>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                    <CardTitle className="text-sm font-medium">Control Limits</CardTitle>
                                    <Activity className="h-4 w-4 text-muted-foreground" />
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold">
                                        {spcData.control_limits.cl.toFixed(1)}%
                                    </div>
                                    <p className="text-xs text-muted-foreground">
                                        UCL: {spcData.control_limits.ucl.toFixed(1)}% | LCL: {spcData.control_limits.lcl.toFixed(1)}%
                                    </p>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                    <CardTitle className="text-sm font-medium">Out of Control</CardTitle>
                                    <AlertTriangle className="h-4 w-4 text-destructive" />
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold text-destructive">
                                        {spcData.summary.out_of_control_count}
                                    </div>
                                    <p className="text-xs text-muted-foreground">
                                        {spcData.summary.out_of_control_rate.toFixed(1)}% of points
                                    </p>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                    <CardTitle className="text-sm font-medium">Std Deviation</CardTitle>
                                    <TrendingUp className="h-4 w-4 text-muted-foreground" />
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold">
                                        {spcData.control_limits.std_dev.toFixed(2)}%
                                    </div>
                                    <p className="text-xs text-muted-foreground">
                                        Process variation
                                    </p>
                                </CardContent>
                            </Card>
                        </div>
                    )}

                    {/* Control Chart */}
                    <Card className="mb-8">
                        <CardHeader>
                            <CardTitle>Defect Rate Control Chart</CardTitle>
                            <CardDescription>
                                Daily defect rates with control limits and rule violations highlighted
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            {spcData && (
                                <ResponsiveContainer width="100%" height={450}>
                                    <LineChart data={spcData.data}>
                                        <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                                        <XAxis
                                            dataKey="date"
                                            tick={{ fontSize: 12 }}
                                            tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                                        />
                                        <YAxis
                                            domain={[0, Math.max(spcData.control_limits.ucl * 1.2, 100)]}
                                            tick={{ fontSize: 12 }}
                                            tickFormatter={(value) => `${value}%`}
                                        />
                                        <Tooltip content={<CustomTooltip />} />
                                        <Legend />

                                        {/* Zone Areas */}
                                        <ReferenceArea
                                            y1={spcData.control_limits.cl - spcData.control_limits.std_dev}
                                            y2={spcData.control_limits.cl + spcData.control_limits.std_dev}
                                            fill="#22c55e"
                                            fillOpacity={0.1}
                                        />
                                        <ReferenceArea
                                            y1={spcData.control_limits.cl + spcData.control_limits.std_dev}
                                            y2={spcData.control_limits.cl + 2 * spcData.control_limits.std_dev}
                                            fill="#eab308"
                                            fillOpacity={0.1}
                                        />
                                        <ReferenceArea
                                            y1={spcData.control_limits.cl + 2 * spcData.control_limits.std_dev}
                                            y2={spcData.control_limits.ucl}
                                            fill="#ef4444"
                                            fillOpacity={0.1}
                                        />

                                        {/* Control Lines */}
                                        <ReferenceLine
                                            y={spcData.control_limits.ucl}
                                            stroke="#ef4444"
                                            strokeDasharray="5 5"
                                            label={{ value: "UCL", position: "right", fill: "#ef4444" }}
                                        />
                                        <ReferenceLine
                                            y={spcData.control_limits.cl}
                                            stroke="#00d4ff"
                                            label={{ value: "CL", position: "right", fill: "#00d4ff" }}
                                        />
                                        <ReferenceLine
                                            y={spcData.control_limits.lcl}
                                            stroke="#ef4444"
                                            strokeDasharray="5 5"
                                            label={{ value: "LCL", position: "right", fill: "#ef4444" }}
                                        />

                                        {/* Data Line */}
                                        <Line
                                            type="monotone"
                                            dataKey="value"
                                            stroke="#00d4ff"
                                            strokeWidth={2}
                                            dot={(props: any) => {
                                                const point = props.payload as SPCDataPoint;
                                                const isViolation = point.is_out_of_control;
                                                return (
                                                    <circle
                                                        key={`dot-${props.index}`}
                                                        cx={props.cx}
                                                        cy={props.cy}
                                                        r={isViolation ? 8 : 4}
                                                        fill={isViolation ? "#ef4444" : "#00d4ff"}
                                                        stroke={isViolation ? "#fff" : "none"}
                                                        strokeWidth={2}
                                                    />
                                                );
                                            }}
                                            name="Defect Rate (%)"
                                        />
                                    </LineChart>
                                </ResponsiveContainer>
                            )}
                        </CardContent>
                    </Card>

                    {/* Western Electric Rules Legend */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Western Electric Rules</CardTitle>
                            <CardDescription>Rules used to detect out-of-control conditions</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="grid md:grid-cols-2 gap-4">
                                <div className="p-4 border rounded-lg">
                                    <div className="flex items-center gap-2 mb-2">
                                        <Badge variant="destructive">Rule 1</Badge>
                                        <span className="font-semibold">Critical</span>
                                    </div>
                                    <p className="text-sm text-muted-foreground">
                                        One point beyond 3σ (control limits)
                                    </p>
                                    {spcData?.summary.rule_violations[1] && (
                                        <p className="text-sm text-destructive mt-1">
                                            {spcData.summary.rule_violations[1]} violations detected
                                        </p>
                                    )}
                                </div>
                                <div className="p-4 border rounded-lg">
                                    <div className="flex items-center gap-2 mb-2">
                                        <Badge variant="secondary" className="bg-orange-500">Rule 2</Badge>
                                        <span className="font-semibold">High</span>
                                    </div>
                                    <p className="text-sm text-muted-foreground">
                                        Two of three consecutive points beyond 2σ (same side)
                                    </p>
                                    {spcData?.summary.rule_violations[2] && (
                                        <p className="text-sm text-orange-500 mt-1">
                                            {spcData.summary.rule_violations[2]} violations detected
                                        </p>
                                    )}
                                </div>
                                <div className="p-4 border rounded-lg">
                                    <div className="flex items-center gap-2 mb-2">
                                        <Badge variant="secondary" className="bg-yellow-500">Rule 3</Badge>
                                        <span className="font-semibold">Medium</span>
                                    </div>
                                    <p className="text-sm text-muted-foreground">
                                        Four of five consecutive points beyond 1σ (same side)
                                    </p>
                                    {spcData?.summary.rule_violations[3] && (
                                        <p className="text-sm text-yellow-500 mt-1">
                                            {spcData.summary.rule_violations[3]} violations detected
                                        </p>
                                    )}
                                </div>
                                <div className="p-4 border rounded-lg">
                                    <div className="flex items-center gap-2 mb-2">
                                        <Badge variant="secondary">Rule 4</Badge>
                                        <span className="font-semibold">Medium</span>
                                    </div>
                                    <p className="text-sm text-muted-foreground">
                                        Eight consecutive points on same side of center line
                                    </p>
                                    {spcData?.summary.rule_violations[4] && (
                                        <p className="text-sm mt-1">
                                            {spcData.summary.rule_violations[4]} violations detected
                                        </p>
                                    )}
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </>
    );
}
