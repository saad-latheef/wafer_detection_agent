"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AppSidebar } from "@/components/layout/AppSidebar";

interface HistoryRecord {
  id: number;
  waferId: string;
  fileName: string;
  toolId: string;
  chamberId: string;
  processedAt: string;
  predictedClass: string;
  confidence: number;
  finalVerdict: string;
  severity: string;
}

export default function HistoryPage() {
  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const response = await fetch("http://localhost:8000/api/history?limit=50");
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setRecords(data.records || []);
      setError(null);
    } catch (err) {
      console.error("Failed to fetch history:", err);
      setError(err instanceof Error ? err.message : "Failed to load history");
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case "critical": return "destructive";
      case "high": return "destructive";
      case "medium": return "default";
      case "low": return "secondary";
      default: return "outline";
    }
  };

  const getVerdictColor = (verdict: string) => {
    return verdict === "FAIL" ? "destructive" : "default";
  };

  return (
    <div className="flex min-h-screen bg-background">
      <AppSidebar currentPage="history" />
      
      <main className="flex-1 ml-64 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold tracking-tight">Scan History</h1>
            <p className="text-muted-foreground mt-2">
              View all wafer analysis records
            </p>
          </div>

          {loading && (
            <Card>
              <CardContent className="p-12">
                <div className="text-center text-muted-foreground">
                  Loading history...
                </div>
              </CardContent>
            </Card>
          )}

          {error && (
            <Card className="border-destructive">
              <CardContent className="p-12">
                <div className="text-center text-destructive">
                  Error: {error}
                </div>
              </CardContent>
            </Card>
          )}

          {!loading && !error && records.length === 0 && (
            <Card>
              <CardContent className="p-12">
                <div className="text-center text-muted-foreground">
                  No scan history found. Upload a wafer to get started.
                </div>
              </CardContent>
            </Card>
          )}

          {!loading && !error && records.length > 0 && (
            <div className="space-y-4">
              {records.map((record) => (
                <Card key={record.id} className="hover:shadow-md transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="text-lg">{record.waferId}</CardTitle>
                        <CardDescription>{record.fileName}</CardDescription>
                      </div>
                      <div className="flex gap-2">
                        <Badge variant={getVerdictColor(record.finalVerdict)}>
                          {record.finalVerdict}
                        </Badge>
                        {record.severity && (
                          <Badge variant={getSeverityColor(record.severity)}>
                            {record.severity}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Predicted Class</p>
                        <p className="font-medium">{record.predictedClass}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Confidence</p>
                        <p className="font-medium">{(record.confidence * 100).toFixed(2)}%</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Tool ID</p>
                        <p className="font-medium">{record.toolId || "N/A"}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Processed At</p>
                        <p className="font-medium">
                          {record.processedAt 
                            ? new Date(record.processedAt).toLocaleString()
                            : "N/A"}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
