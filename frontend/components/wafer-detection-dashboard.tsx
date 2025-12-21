"use client"

import type React from "react"
import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import {
  Upload,
  CheckCircle2,
  Activity,
  FileText,
  Cpu,
  Brain,
  TrendingUp,
  AlertTriangle,
  Package,
  ChevronLeft,
  Printer,
  Download,
  ArrowLeft,
} from "lucide-react"
import { cn } from "@/lib/utils"

type DefectPattern = "Center" | "Donut" | "Edge-Loc" | "Edge-Ring" | "Loc" | "Random" | "Scratch" | "Near-full" | "None"

interface PatternProbability {
  pattern: DefectPattern
  probability: number
}

interface AgentResult {
  name: string
  model: string
  topPattern: DefectPattern
  topProbabilities: PatternProbability[]
  confidence: number
  qualityFlag: string | null
  description: string
  rootCauses: string[]
  actionSuggestions: string[]
  icon: React.ReactNode
  heatmapUrl?: string
}

// Updated LotAnalysis interface
interface LotAnalysis {
  lotId: string
  totalWafers: number
  defectiveWafers: number
  yieldRate: number
  defectDistribution: Array<{
    name: DefectPattern
    count: number
    severity: "Low" | "Medium" | "High"
  }>
  systematicIssues: Array<{
    pattern: string
    frequency: number
    trend: string
    rootCause: string
  }>
  recommendations: Array<{
    priority: "Critical" | "High" | "Medium"
    action: string
    estimatedImpact: string
  }>
}

// Detailed interfaces for agent data
interface IngestionDetails {
  waferMapShape: number[]
  tensorShape: number[]
  nonWaferCount: number
  normalCount: number
  defectCount: number
}

interface AnalysisDetails {
  consistencyScore: number
  issuesFound: string[]
  recommendation: string
  majorIssues: Array<{ class: string; probability: number }>
}

interface ValidationDetails {
  attempts: number
  maxAttempts: number
  criteriaChecks: Array<{ name: string; passed: boolean }>
  passed: boolean
}

interface TriggerAction {
  alertSent: boolean
  recipient: string
  subject: string
  severity: string
  actions: string[]
}

// New interface for individual wafer analysis
interface WaferAnalysis {
  waferId: string
  image: string
  fileName: string
  detectedPattern: DefectPattern
  agentResults: AgentResult[]
  finalVerdict: "PASS" | "FAIL"
  confidence: number
  fullProbabilityDistribution: Record<string, number>
  explanation: string
  severity: string
  // Detailed agent data
  ingestionDetails?: IngestionDetails
  analysisDetails?: AnalysisDetails
  validationDetails?: ValidationDetails
  triggerAction?: TriggerAction
  modelUsed?: string
  deviceUsed?: string
}

// Default AgentResult interface with properties for ProbabilityResult and Probability
type ProbabilityResult = {
  pattern: DefectPattern
  probability: number
}

interface WaferDetectionDashboardProps {
  onBack?: () => void
}

export function WaferDetectionDashboard({ onBack }: WaferDetectionDashboardProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [uploadedImages, setUploadedImages] = useState<Array<{ id: string; url: string; file?: File; fileName: string }>>([])
  const [currentWaferId, setCurrentWaferId] = useState<string | null>(null)
  const [selectedWafer, setSelectedWafer] = useState<WaferAnalysis | null>(null)
  const [lotAnalysis, setLotAnalysis] = useState<LotAnalysis | null>(null)
  const [showLotAnalysis, setShowLotAnalysis] = useState(false)

  // Trend Analysis State
  const [trendAnalysisResult, setTrendAnalysisResult] = useState<string>("")
  const [isTrendAnalyzing, setIsTrendAnalyzing] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [waferAnalyses, setWaferAnalyses] = useState<WaferAnalysis[]>([])
  const [analysisComplete, setAnalysisComplete] = useState(false)
  const [fullProbDist, setFullProbDist] = useState<Record<string, number>>({})
  const [explanation, setExplanation] = useState<string>("")

  // New state for defect grouping and individual view
  const [selectedDefectFilter, setSelectedDefectFilter] = useState<DefectPattern | "all">("all")
  const [viewMode, setViewMode] = useState<"summary" | "grouped" | "individual">("summary")

  const [agentResults, setAgentResults] = useState<AgentResult[]>([
    {
      name: "CNN Classifier",
      model: "k_cross_CNN (Pattern Detection)",
      topPattern: "None",
      topProbabilities: [],
      confidence: 0,
      qualityFlag: null,
      description: "Awaiting wafer map upload to begin analysis...",
      rootCauses: [],
      actionSuggestions: [],
      icon: <Cpu className="h-5 w-5" />,
    },
    {
      name: "Analysis Agent",
      model: "Statistical Analysis Module",
      topPattern: "None",
      topProbabilities: [],
      confidence: 0,
      qualityFlag: null,
      description: "Awaiting wafer map upload to begin analysis...",
      rootCauses: [],
      actionSuggestions: [],
      icon: <Brain className="h-5 w-5" />,
    },
    {
      name: "Validation Agent",
      model: "Quality Assurance Module",
      topPattern: "None",
      topProbabilities: [],
      confidence: 0,
      qualityFlag: null,
      description: "Awaiting wafer map upload to begin analysis...",
      rootCauses: [],
      actionSuggestions: [],
      icon: <FileText className="h-5 w-5" />,
    },
  ])


  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (files && files.length > 0) {
      const newImages: Array<{ id: string; url: string; file?: File; fileName: string }> = []

      Array.from(files).forEach((file, index) => {
        const reader = new FileReader()
        reader.onloadend = () => {
          const waferId = `W-${Math.floor(Math.random() * 10000)}-X${index + 1}`
          newImages.push({
            id: waferId,
            url: reader.result as string,
            file: file,
            fileName: file.name,
          })

          if (newImages.length === files.length) {
            setUploadedImages((prev) => [...prev, ...newImages])
            setCurrentWaferId(newImages[0].id)
          }
        }
        reader.readAsDataURL(file)
      })
    }
  }

  // Generate a mock AgentResult
  const generateAgentResult = (pattern: string, agentIndex: number): AgentResult => {
    const patterns = ["None", "Edge-Ring", "Center", "Edge-Loc", "Scratch", "Random", "Donut", "Near-full"]
    const topProbs: ProbabilityResult[] = patterns
      .slice(0, 3)
      .map((p, i) => ({
        pattern:
          i === 0
            ? (pattern as DefectPattern)
            : (patterns[Math.floor(Math.random() * patterns.length)] as DefectPattern),
        probability: i === 0 ? Math.random() * 0.3 + 0.65 : Math.random() * 0.25,
      }))
      .sort((a, b) => b.probability - a.probability)

    const confidence = topProbs[0].probability * 100
    const qualityFlag = confidence < 75 ? "Review Required - Ambiguous" : null

    const agentNames = ["ViT Model", "Gemini Pro Vision", "ChatGPT Vision"]
    const models = ["Custom Vision Transformer", "Visual Analysis (GPT-4)", "Multimodal Analysis (GPT-4o)"]
    const icons = [
      <Cpu className="h-5 w-5" key={0} />,
      <Brain className="h-5 w-5" key={1} />,
      <FileText className="h-5 w-5" key={2} />,
    ]

    return {
      name: agentNames[agentIndex],
      model: models[agentIndex],
      topPattern: pattern as DefectPattern,
      topProbabilities: topProbs,
      confidence,
      qualityFlag,
      description:
        pattern === "None"
          ? "No significant defect patterns detected. All quality metrics within specification."
          : `Detected ${pattern} defect pattern with ${confidence.toFixed(1)}% confidence.`,
      rootCauses:
        pattern !== "None" ? ["Process drift in deposition phase", "Contamination from handling equipment"] : [],
      actionSuggestions:
        pattern !== "None"
          ? ["Immediate lot hold recommended", "Escalate to process engineering team"]
          : ["Continue production monitoring", "Standard quality gate passage"],
      icon: icons[agentIndex],
    }
  }

  const runBatchAnalysis = async () => {
    if (uploadedImages.length === 0) return

    setIsAnalyzing(true)
    setViewMode("summary")
    setSelectedWafer(null)
    const analyses: WaferAnalysis[] = []

    for (const wafer of uploadedImages) {
      try {
        // Call real API
        const formData = new FormData()
        if (wafer.file) {
          formData.append('file', wafer.file)
        }

        const response = await fetch('http://localhost:8000/api/analyze', {
          method: 'POST',
          body: formData,
        })

        if (!response.ok) {
          throw new Error('API request failed')
        }

        const data = await response.json()

        // Map API response to AgentResult format with icons
        const agentResultsWithIcons = data.agentResults.map((agent: AgentResult, idx: number) => ({
          ...agent,
          icon: idx === 0 ? <Cpu className="h-5 w-5" key={idx} />
            : idx === 1 ? <Brain className="h-5 w-5" key={idx} />
              : <FileText className="h-5 w-5" key={idx} />
        }))

        // Get detected pattern from first agent result
        const detectedPattern = data.agentResults[0]?.topPattern || "None"

        analyses.push({
          waferId: data.waferId,
          image: wafer.url,
          fileName: data.fileName || wafer.fileName,
          detectedPattern: detectedPattern as DefectPattern,
          agentResults: agentResultsWithIcons,
          finalVerdict: data.finalVerdict as "PASS" | "FAIL",
          confidence: data.confidence,
          fullProbabilityDistribution: data.fullProbabilityDistribution,
          explanation: data.explanation,
          severity: data.severity,
          ingestionDetails: data.ingestionDetails,
          analysisDetails: data.analysisDetails,
          validationDetails: data.validationDetails,
          triggerAction: data.triggerAction,
          modelUsed: data.modelUsed,
          deviceUsed: data.deviceUsed,
        })
      } catch (error) {
        console.error('Analysis failed:', error)
        analyses.push({
          waferId: wafer.id,
          image: wafer.url,
          fileName: wafer.fileName,
          detectedPattern: "None" as DefectPattern,
          agentResults: [],
          finalVerdict: "FAIL" as const,
          confidence: 0,
          fullProbabilityDistribution: {},
          explanation: "Analysis failed - please try again",
          severity: "None",
        })
      }
    }

    setWaferAnalyses(analyses)
    setIsAnalyzing(false)
    setShowLotAnalysis(true)

    // Generate lot-level statistics
    generateLotAnalysis(analyses)
  }

  const generateLotAnalysis = (analyses: WaferAnalysis[]) => {
    // Aggregate real defect patterns from actual analyses
    const patternCounts = new Map<string, number>()
    analyses.forEach(wafer => {
      const pattern = wafer.detectedPattern
      patternCounts.set(pattern, (patternCounts.get(pattern) || 0) + 1)
    })

    // Convert to defect distribution format
    const defectDistribution = Array.from(patternCounts.entries())
      .filter(([name]) => name !== "None" && name !== "none")
      .map(([name, count]) => ({
        name: name as DefectPattern,
        count,
        severity: (count > 3 ? "High" : count > 1 ? "Medium" : "Low") as "High" | "Medium" | "Low"
      }))
      .sort((a, b) => b.count - a.count)

    const totalDefects = analyses.filter((a) => a.finalVerdict === "FAIL").length
    const passCount = analyses.filter((a) => a.finalVerdict === "PASS").length

    // Get top defect patterns for recommendations
    const topDefects = defectDistribution.slice(0, 2)

    const lotData: LotAnalysis = {
      lotId: `LOT-${Math.floor(Math.random() * 1000) + 1}`,
      totalWafers: analyses.length,
      defectiveWafers: totalDefects,
      yieldRate: analyses.length > 0 ? (passCount / analyses.length) * 100 : 0,
      defectDistribution,
      systematicIssues: topDefects.map(d => ({
        pattern: `${d.name} defects detected`,
        frequency: d.count,
        trend: d.count > 2 ? "Increasing" : "Stable",
        rootCause: `Potential ${d.name.toLowerCase()} pattern issue in processing`,
      })),
      recommendations: topDefects.length > 0 ? topDefects.map((d, i) => ({
        priority: (i === 0 ? "Critical" : "High") as "Critical" | "High" | "Medium",
        action: `Investigate ${d.name} defect source - ${d.count} occurrences`,
        estimatedImpact: `+${Math.min(d.count * 2, 10)}% yield improvement`,
      })) : [{
        priority: "Medium" as const,
        action: "Continue standard monitoring",
        estimatedImpact: "Maintain current yield",
      }],
    }
    setLotAnalysis(lotData)

    // Auto-switch to grouped view when lot analysis is active
    setViewMode("grouped")

    // Trigger Trend Analysis
    const distributionForTrend = Object.fromEntries(patternCounts.entries());
    fetchTrendAnalysis(distributionForTrend)
  }

  const fetchTrendAnalysis = async (distribution: Record<string, number>) => {
    setIsTrendAnalyzing(true)
    try {
      const response = await fetch('http://localhost:8000/api/analyze-lot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ defectDistribution: distribution })
      })

      if (response.ok) {
        const data = await response.json()
        setTrendAnalysisResult(data.analysis)
      } else {
        setTrendAnalysisResult("Unable to generate trend analysis.")
      }
    } catch (e) {
      console.error("Trend analysis failed", e)
      setTrendAnalysisResult("Error connecting to Trend Agent.")
    } finally {
      setIsTrendAnalyzing(false)
    }
  }

  // Generate formatted text report for download
  const generateReport = (wafer: WaferAnalysis) => {
    const timestamp = new Date().toLocaleString()
    const separator = "═".repeat(60)
    const line = "─".repeat(60)

    let report = `
${separator}
              WAFER DETECTION ANALYSIS REPORT
${separator}

Generated: ${timestamp}
Report ID: ${wafer.waferId}

${line}
                    WAFER INFORMATION
${line}

File Name:        ${wafer.fileName}
Wafer ID:         ${wafer.waferId}
Model Used:       ${wafer.modelUsed || "k_cross_CNN.pt"}
Device:           ${wafer.deviceUsed || "CPU"}

${line}
                    ANALYSIS RESULT
${line}

Final Verdict:    ${wafer.finalVerdict}
Detected Pattern: ${wafer.detectedPattern}
Confidence:       ${wafer.confidence.toFixed(1)}%
Severity:         ${wafer.severity}

${line}
                PROBABILITY DISTRIBUTION
${line}

`
    // Add probability distribution
    Object.entries(wafer.fullProbabilityDistribution)
      .sort(([, a], [, b]) => b - a)
      .forEach(([pattern, prob]) => {
        const bar = "█".repeat(Math.floor(prob / 5))
        const isTop = pattern === wafer.detectedPattern ? " ← DETECTED" : ""
        report += `${pattern.padEnd(12)}: ${prob.toFixed(2).padStart(6)}% ${bar}${isTop}\n`
      })

    // Add ingestion details
    if (wafer.ingestionDetails) {
      report += `
${line}
                  INGESTION DETAILS
${line}

Wafer Map Shape:  ${wafer.ingestionDetails.waferMapShape?.join(" × ")}
Tensor Shape:     ${wafer.ingestionDetails.tensorShape?.join(" × ")}
Non-Wafer Pixels: ${wafer.ingestionDetails.nonWaferCount}
Normal Pixels:    ${wafer.ingestionDetails.normalCount}
Defect Pixels:    ${wafer.ingestionDetails.defectCount}
`
    }

    // Add analysis details
    if (wafer.analysisDetails) {
      report += `
${line}
                  ANALYSIS DETAILS
${line}

Consistency Score: ${(wafer.analysisDetails.consistencyScore * 100).toFixed(0)}%
Recommendation:    ${wafer.analysisDetails.recommendation}
Issues Found:      ${wafer.analysisDetails.issuesFound?.length || 0}
`
    }

    // Add validation details
    if (wafer.validationDetails) {
      report += `
${line}
                 VALIDATION DETAILS
${line}

Status:           ${wafer.validationDetails.passed ? "PASSED" : "FAILED"}
Attempts:         ${wafer.validationDetails.attempts}/${wafer.validationDetails.maxAttempts}

Criteria Checks:
`
      wafer.validationDetails.criteriaChecks?.forEach(check => {
        report += `  ${check.passed ? "✓" : "✗"} ${check.name}\n`
      })
    }

    // Add trigger action
    if (wafer.triggerAction) {
      report += `
${line}
                   TRIGGER ACTION
${line}

Alert Sent:       ${wafer.triggerAction.alertSent ? "YES" : "NO"}
Severity:         ${wafer.triggerAction.severity}
${wafer.triggerAction.alertSent ? `Recipient:        ${wafer.triggerAction.recipient}` : ""}

Recommended Actions:
`
      wafer.triggerAction.actions?.forEach((action, i) => {
        report += `  ${i + 1}. ${action}\n`
      })
    }

    // Add agent results
    report += `
${line}
                   AGENT ANALYSIS
${line}

`
    wafer.agentResults.forEach(agent => {
      report += `[${agent.name}] - ${agent.model}
  Pattern: ${agent.topPattern} (${agent.confidence.toFixed(1)}% confidence)
  ${agent.description}
`
      if (agent.rootCauses.length > 0) {
        report += `  Root Causes:\n`
        agent.rootCauses.forEach(cause => {
          report += `    • ${cause}\n`
        })
      }
      if (agent.actionSuggestions.length > 0) {
        report += `  Suggested Actions:\n`
        agent.actionSuggestions.forEach(action => {
          report += `    • ${action}\n`
        })
      }
      report += "\n"
    })

    // Add full explanation
    if (wafer.explanation) {
      report += `
${line}
                 DETAILED EXPLANATION
${line}

${wafer.explanation}
`
    }

    report += `
${separator}
                    END OF REPORT
${separator}
`

    // Download the report
    const blob = new Blob([report], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `wafer-report-${wafer.waferId}-${Date.now()}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const runAnalysis = async () => {
    if (uploadedImages.length === 0) return
    // This function is now superseded by runBatchAnalysis for multiple wafers.
    // It can be kept for single-file upload scenarios if needed, but for now, we'll focus on batch.
    setIsAnalyzing(true)
    setAnalysisComplete(false) // Assuming this state might be needed elsewhere or for consistency.

    const mockResults: AgentResult[] = [
      {
        name: "ViT Model",
        model: "Custom Vision Transformer",
        topPattern: "Edge-Ring",
        topProbabilities: [
          { pattern: "Edge-Ring", probability: 92.3 },
          { pattern: "Edge-Loc", probability: 5.2 },
          { pattern: "Random", probability: 2.1 },
        ],
        confidence: 92.3,
        qualityFlag: null,
        description:
          "Predicted pattern: Edge-Ring (92.3% confidence). This usually indicates issues in edge bead removal, spin coating, or edge-related process non-uniformity.",
        rootCauses: [
          "Edge bead removal (EBR) process deviation",
          "Spin coating non-uniformity at wafer periphery",
          "Chamber edge heating inconsistency",
        ],
        actionSuggestions: [
          "Check EBR tool calibration and nozzle positioning",
          "Verify spin coating recipe parameters",
          "Inspect edge exclusion zone settings",
        ],
        icon: <Cpu className="h-5 w-5" />,
        heatmapUrl: "/wafer-edge-ring-defect-heatmap.jpg",
      },
      {
        name: "Gemini Pro Vision",
        model: "Visual Analysis (GPT-4)",
        topPattern: "Edge-Ring",
        topProbabilities: [
          { pattern: "Edge-Ring", probability: 88.7 },
          { pattern: "Edge-Loc", probability: 7.8 },
          { pattern: "None", probability: 2.5 },
        ],
        confidence: 88.7,
        qualityFlag: null,
        description:
          "Predicted pattern: Edge-Ring (88.7% confidence). Visual analysis confirms peripheral defect concentration consistent with edge-related processing issues.",
        rootCauses: ["Photoresist edge accumulation", "Plasma etching edge effects", "Wafer handling edge damage"],
        actionSuggestions: [
          "Review photoresist dispense and edge coverage",
          "Analyze plasma uniformity across wafer",
          "Inspect robotic handler edge contact points",
        ],
        icon: <Brain className="h-5 w-5" />,
      },
      {
        name: "ChatGPT Vision",
        model: "Multimodal Analysis (GPT-4o)",
        topPattern: "Center",
        topProbabilities: [
          { pattern: "Center", probability: 78.4 },
          { pattern: "Edge-Ring", probability: 15.2 },
          { pattern: "Random", probability: 4.1 },
        ],
        confidence: 78.4,
        qualityFlag: "⚠️ Mixed pattern detected - confidence spread across multiple classes",
        description:
          "Predicted pattern: Center (78.4% confidence). However, significant secondary probability for Edge-Ring suggests possible mixed defect types or transitional pattern.",
        rootCauses: [
          "Focus or exposure center bias",
          "Chuck temperature center gradient",
          "Gas flow distribution center concentration",
        ],
        actionSuggestions: [
          "Verify stepper focus calibration",
          "Check chuck thermal uniformity",
          "Analyze process gas flow patterns",
        ],
        icon: <FileText className="h-5 w-5" />,
      },
    ]

    const mockLotAnalysis: LotAnalysis = {
      lotId: "LOT-2024-A127",
      totalWafers: 25,
      defectiveWafers: 10,
      yieldRate: 76.0,
      defectDistribution: [
        { name: "Edge-Ring", count: 10, severity: "High" },
        { name: "Center", count: 4, severity: "Medium" },
        { name: "Random", count: 3, severity: "Low" },
        { name: "Edge-Loc", count: 2, severity: "Medium" },
        { name: "None", count: 6, severity: "Low" },
      ],
      systematicIssues: [
        {
          pattern: "Edge-Ring clustering in Lot 2394",
          frequency: 12,
          trend: "Increasing",
          rootCause: "Possible edge bead removal (EBR) process drift",
        },
        {
          pattern: "Center defects on East chamber",
          frequency: 8,
          trend: "Stable",
          rootCause: "Wafer chuck temperature uniformity issue",
        },
      ],
      recommendations: [
        {
          priority: "Critical",
          action: "Recalibrate EBR module - Edge defects increasing",
          estimatedImpact: "+8% yield improvement",
        },
        {
          priority: "High",
          action: "PM check on East chamber chuck heater",
          estimatedImpact: "+3% yield improvement",
        },
        {
          priority: "Medium",
          action: "Review photoresist coating parameters",
          estimatedImpact: "+2% defect reduction",
        },
      ],
    }

    // Simulate staggered analysis completion
    for (let i = 0; i < mockResults.length; i++) {
      await new Promise((resolve) => setTimeout(resolve, 1200 + Math.random() * 800))
      setAgentResults((prev) => {
        const newResults = [...prev]
        newResults[i] = mockResults[i]
        return newResults
      })
    }

    setLotAnalysis(mockLotAnalysis)
    setIsAnalyzing(false)
    setAnalysisComplete(true)
  }

  const getFinalVerdict = () => {
    if (!analysisComplete) return null

    const patternCounts = new Map<DefectPattern, number>()
    agentResults.forEach((agent) => {
      const count = patternCounts.get(agent.topPattern) || 0
      patternCounts.set(agent.topPattern, count + 1)
    })

    let maxCount = 0
    let consensusPattern: DefectPattern = "None"
    patternCounts.forEach((count, pattern) => {
      if (count > maxCount) {
        maxCount = count
        consensusPattern = pattern
      }
    })

    const avgConfidence = agentResults.reduce((sum, a) => sum + a.confidence, 0) / agentResults.length
    const hasDefect = consensusPattern !== "None"

    return {
      pattern: consensusPattern,
      confidence: avgConfidence,
      hasDefect,
      riskLevel: hasDefect && avgConfidence > 85 ? "High" : hasDefect ? "Medium" : "Low",
    }
  }

  const verdict = getFinalVerdict()
  const getPatternColor = (pattern: DefectPattern) => {
    const colors: Record<DefectPattern, string> = {
      Center: "text-chart-2",
      Donut: "text-chart-3",
      "Edge-Loc": "text-destructive",
      "Edge-Ring": "text-accent",
      Loc: "text-chart-5",
      Random: "text-muted-foreground",
      Scratch: "text-chart-1",
      "Near-full": "text-destructive",
      None: "text-chart-4",
    }
    return colors[pattern] || "text-foreground"
  }

  return (
    <div className="flex min-h-screen bg-background">
      {/* Sidebar */}
      <aside
        className={cn(
          "fixed left-0 top-0 h-screen border-r border-border bg-sidebar transition-all duration-300 z-10",
          sidebarCollapsed ? "w-16" : "w-64",
        )}
      >
        <div className="flex flex-col h-full p-6">
          <div className="mb-8">
            <div className={cn("flex items-center mb-2", sidebarCollapsed ? "justify-center" : "gap-3")}>
              <div className="h-10 w-10 rounded-lg bg-primary flex items-center justify-center shrink-0">
                <Activity className="h-6 w-6 text-primary-foreground" />
              </div>
              {!sidebarCollapsed && (
                <div>
                  <h1 className="text-lg font-bold text-sidebar-foreground">WaferDetect</h1>
                  <p className="text-xs text-sidebar-foreground/60">v24.1 Enterprise</p>
                </div>
              )}
            </div>
          </div>

          <nav className="space-y-2">
            {onBack && (
              <Button
                variant="ghost"
                onClick={onBack}
                className={cn(
                  "w-full text-sidebar-foreground hover:text-sidebar-foreground hover:bg-sidebar-accent mb-4",
                  sidebarCollapsed ? "justify-center px-0" : "justify-start",
                )}
              >
                <ArrowLeft className={cn("h-4 w-4", !sidebarCollapsed && "mr-2")} />
                {!sidebarCollapsed && "Back to Home"}
              </Button>
            )}
            <Button
              variant="secondary"
              className={cn("w-full", sidebarCollapsed ? "justify-center px-0" : "justify-start")}
            >
              <Activity className={cn("h-4 w-4", !sidebarCollapsed && "mr-2")} />
              {!sidebarCollapsed && "Dashboard"}
            </Button>
            <Button
              variant="ghost"
              className={cn(
                "w-full text-sidebar-foreground hover:text-sidebar-foreground hover:bg-sidebar-accent",
                sidebarCollapsed ? "justify-center px-0" : "justify-start",
              )}
            >
              <FileText className={cn("h-4 w-4", !sidebarCollapsed && "mr-2")} />
              {!sidebarCollapsed && "Scan History"}
            </Button>
            <Button
              variant="ghost"
              onClick={() => window.location.href = '/analytics'}
              className={cn(
                "w-full text-sidebar-foreground hover:text-sidebar-foreground hover:bg-sidebar-accent",
                sidebarCollapsed ? "justify-center px-0" : "justify-start",
              )}
            >
              <TrendingUp className={cn("h-4 w-4", !sidebarCollapsed && "mr-2")} />
              {!sidebarCollapsed && "Analytics"}
            </Button>
            <Button
              variant="ghost"
              className={cn(
                "w-full text-sidebar-foreground hover:text-sidebar-foreground hover:bg-sidebar-accent",
                sidebarCollapsed ? "justify-center px-0" : "justify-start",
              )}
            >
              <Cpu className={cn("h-4 w-4", !sidebarCollapsed && "mr-2")} />
              {!sidebarCollapsed && "Model Config"}
            </Button>
          </nav>

          <div className="mt-auto pt-8">
            {!sidebarCollapsed && (
              <>
                <div className="flex items-center gap-2 text-sm">
                  <div className="h-2 w-2 rounded-full bg-chart-4 animate-pulse" />
                  <span className="text-sidebar-foreground/80">System Operational</span>
                </div>
                <p className="text-xs text-sidebar-foreground/60 mt-1">All agents online</p>
              </>
            )}
            {sidebarCollapsed && (
              <div className="flex justify-center">
                <div className="h-2 w-2 rounded-full bg-chart-4 animate-pulse" />
              </div>
            )}
          </div>
        </div>

        <Button
          variant="ghost"
          size="icon"
          className="absolute -right-3 top-6 h-6 w-6 rounded-full border border-border bg-background shadow-sm hover:bg-accent"
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
        >
          <ChevronLeft className={cn("h-4 w-4 transition-transform duration-300", sidebarCollapsed && "rotate-180")} />
        </Button>
      </aside>

      {/* Main Content */}
      <main
        className={cn("flex-1 p-8 overflow-auto transition-all duration-300", sidebarCollapsed ? "ml-16" : "ml-64")}
      >
        {/* Hero Section */}
        <div className="mb-8 rounded-xl bg-gradient-to-r from-card to-secondary p-8 border border-border">
          <Badge className="mb-4 bg-primary/20 text-primary border-primary/30">
            <Activity className="mr-1 h-3 w-3" />
            LIVE MONITORING
          </Badge>
          <h2 className="text-4xl font-bold mb-2 text-balance">Fault Detection Dashboard</h2>
          <p className="text-muted-foreground text-lg">
            Real-time analysis of silicon wafer integrity using multi-agent AI consensus.
          </p>
        </div>

        {/* Data Ingestion */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Data Ingestion</span>
              <span className="text-sm font-normal text-muted-foreground">Supported formats: NPY (wafer maps)</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Upload Area */}
              <div className="flex flex-col gap-4">
                <div className="relative">
                  <input
                    type="file"
                    accept=".npy"
                    multiple
                    onChange={handleFileUpload}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload">
                    <div className="cursor-pointer border-2 border-dashed border-border rounded-lg p-8 hover:border-primary transition-colors flex flex-col items-center justify-center min-h-[300px] bg-secondary/30">
                      {uploadedImages.length > 0 ? (
                        <div className="w-full">
                          <div className="grid grid-cols-3 gap-2 mb-4">
                            {uploadedImages.slice(0, 6).map((wafer) => (
                              <div key={wafer.id} className="relative group">
                                <img
                                  src={wafer.url || "/placeholder.svg"}
                                  alt={wafer.id}
                                  className="rounded-lg w-full h-24 object-cover border-2 border-border group-hover:border-primary transition-colors"
                                />
                                <div className="absolute bottom-1 left-1 bg-card/90 backdrop-blur px-2 py-0.5 rounded text-[10px] font-mono">
                                  {wafer.id}
                                </div>
                              </div>
                            ))}
                          </div>
                          {uploadedImages.length > 6 && (
                            <p className="text-center text-sm text-muted-foreground">
                              +{uploadedImages.length - 6} more wafers
                            </p>
                          )}
                        </div>
                      ) : (
                        <>
                          <Upload className="h-12 w-12 text-muted-foreground mb-4" />
                          <p className="text-sm text-center text-muted-foreground">
                            Drop wafer scans here or click to browse
                          </p>
                          <p className="text-xs text-center text-muted-foreground mt-2">
                            Select multiple files for batch analysis
                          </p>
                        </>
                      )}
                    </div>
                  </label>
                </div>
              </div>

              {/* Upload Info */}
              <div className="flex flex-col gap-4">
                <div>
                  <h3 className="text-lg font-semibold mb-2">Upload Wafer Maps</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    Drag & drop wafer maps (.npy files) here to begin analysis with our CNN model pipeline.
                  </p>
                </div>

                <div className="flex gap-3">
                  <Button
                    onClick={runBatchAnalysis}
                    disabled={uploadedImages.length === 0 || isAnalyzing}
                    className="bg-accent text-accent-foreground hover:bg-accent/90"
                  >
                    <Activity className="mr-2 h-4 w-4" />
                    {isAnalyzing
                      ? "Analyzing..."
                      : `Analyze ${uploadedImages.length} Wafer${uploadedImages.length !== 1 ? "s" : ""}`}
                  </Button>
                  <Button variant="outline" asChild>
                    <label htmlFor="file-upload" className="cursor-pointer">
                      <Upload className="mr-2 h-4 w-4" />
                      Add More Files
                    </label>
                  </Button>
                </div>

                {uploadedImages.length > 0 && (
                  <div className="mt-4 p-4 bg-secondary/50 rounded-lg border border-border">
                    <p className="text-xs text-muted-foreground mb-2">Batch Details</p>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Total Wafers:</span>
                        <span className="font-mono">{uploadedImages.length}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Format:</span>
                        <span className="font-mono">PNG</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Status:</span>
                        <span className={cn(isAnalyzing && "animate-pulse")}>
                          {isAnalyzing ? "Processing..." : waferAnalyses.length > 0 ? "Complete" : "Ready"}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Lot Analysis Section (Prioritized) */}
        {showLotAnalysis && lotAnalysis && (
          <div className="mb-8">
            <h3 className="text-2xl font-bold mb-4">Lot-Level Analysis</h3>

            {/* Statistics Overview */}
            <div className="grid md:grid-cols-4 gap-4 mb-6">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between mb-2">
                    <Package className="h-8 w-8 text-primary" />
                    <span className="text-3xl font-bold">{lotAnalysis.totalWafers}</span>
                  </div>
                  <p className="text-sm text-muted-foreground">Total Wafers</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between mb-2">
                    <AlertTriangle className="h-8 w-8 text-red-400" />
                    <span className="text-3xl font-bold text-red-400">{lotAnalysis.defectiveWafers}</span>
                  </div>
                  <p className="text-sm text-muted-foreground">Defective Wafers</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between mb-2">
                    <TrendingUp className="h-8 w-8 text-green-400" />
                    <span className="text-3xl font-bold text-green-400">{lotAnalysis.yieldRate.toFixed(1)}%</span>
                  </div>
                  <p className="text-sm text-muted-foreground">Yield Rate</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between mb-2">
                    <CheckCircle2 className="h-8 w-8 text-green-400" />
                    <span className="text-3xl font-bold text-green-400">
                      {lotAnalysis.totalWafers - lotAnalysis.defectiveWafers}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">Pass Count</p>
                </CardContent>
              </Card>
            </div>

            <div className="grid lg:grid-cols-2 gap-6">
              {/* Pareto Chart */}
              <Card>
                <CardHeader>
                  <CardTitle>Defect Pattern Distribution</CardTitle>
                  <CardDescription>
                    Lot {lotAnalysis.lotId} - {lotAnalysis.totalWafers} wafers
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {lotAnalysis.defectDistribution
                      .sort((a, b) => b.count - a.count)
                      .map((defect, idx) => {
                        const percentage = (defect.count / lotAnalysis.totalWafers) * 100
                        return (
                          <div key={idx}>
                            <div className="flex justify-between text-sm mb-1">
                              <span className={cn("font-semibold", getPatternColor(defect.name))}>{defect.name}</span>
                              <span className="font-mono text-muted-foreground">
                                {defect.count} wafers ({percentage.toFixed(0)}%)
                              </span>
                            </div>
                            <Progress value={percentage} className="h-2.5" />
                          </div>
                        )
                      })}
                  </div>

                  <div className="mt-6 pt-4 border-t border-border">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Estimated Yield</p>
                        <p className="text-2xl font-bold text-chart-4">{lotAnalysis.yieldRate.toFixed(1)}%</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Good Die Rate</p>
                        <p className="text-2xl font-bold text-chart-4">~82%</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Systematic Issue Detection (LLM Powered) */}
              <Card>
                <CardHeader>
                  <CardTitle>Systematic Issue Detection</CardTitle>
                  <CardDescription>Trend analysis & recommendations</CardDescription>
                </CardHeader>
                <CardContent>
                  {isTrendAnalyzing ? (
                    <div className="flex flex-col items-center justify-center py-8 space-y-4">
                      <div className="h-8 w-8 rounded-full border-4 border-primary border-t-transparent animate-spin" />
                      <p className="text-sm text-muted-foreground animate-pulse">Running Root Cause Analysis...</p>
                    </div>
                  ) : trendAnalysisResult ? (
                    <div className="space-y-4">
                      <div className={cn(
                        "p-4 rounded-lg border",
                        trendAnalysisResult.includes("NO DEFECTS") ? "bg-green-500/10 border-green-500/30" : "bg-destructive/10 border-destructive/30"
                      )}>
                        <h4 className={cn(
                          "font-bold flex items-center gap-2 mb-2",
                          trendAnalysisResult.includes("NO DEFECTS") ? "text-green-400" : "text-destructive"
                        )}>
                          {trendAnalysisResult.includes("NO DEFECTS") ? <CheckCircle2 className="h-5 w-5" /> : <AlertTriangle className="h-5 w-5" />}
                          Analysis Result
                        </h4>
                        <pre className="text-sm whitespace-pre-wrap font-sans text-foreground/90">
                          {trendAnalysisResult}
                        </pre>
                      </div>
                    </div>
                  ) : (
                    <div className="p-4 rounded-lg border border-destructive/30 bg-destructive/10">
                      <h4 className="font-bold text-destructive mb-1 flex items-center gap-2">
                        <AlertTriangle className="h-4 w-4" />
                        Systematic Issue Detected
                      </h4>
                      <p className="text-sm text-muted-foreground mb-3">
                        Multiple wafers in this lot share the same defect pattern, indicating a systemic problem.
                      </p>
                    </div>
                  )}

                  {!isTrendAnalyzing && (
                    <div className="mt-4 p-4 rounded-lg bg-secondary/50 border border-border">
                      <h4 className="font-semibold mb-2">Priority Actions</h4>
                      <ul className="space-y-2 text-sm">
                        <li className="flex items-start gap-2">
                          <span className="text-primary mt-0.5">•</span>
                          <span>Auto-generated based on defect distribution via LLM agent.</span>
                        </li>
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* Results Overview (Cards Hidden if Lot Analysis Active) */}
        {!showLotAnalysis && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Wafers</CardTitle>
                <Package className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{uploadedImages.length}</div>
                <p className="text-xs text-muted-foreground">
                  {isAnalyzing ? "Analyzing..." : `${waferAnalyses.length} analyzed`}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Passed</CardTitle>
                <CheckCircle2 className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-500">
                  {waferAnalyses.filter((w) => w.finalVerdict === "PASS").length}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Defective</CardTitle>
                <AlertTriangle className="h-4 w-4 text-destructive" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-destructive">
                  {waferAnalyses.filter((w) => w.finalVerdict === "FAIL").length}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Yield Rate</CardTitle>
                <TrendingUp className="h-4 w-4 text-primary" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {waferAnalyses.length > 0
                    ? (
                      (waferAnalyses.filter((w) => w.finalVerdict === "PASS").length / waferAnalyses.length) *
                      100
                    ).toFixed(1)
                    : "0.0"}
                  %
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Analysis Results Section */}
        {waferAnalyses.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold">Analysis Results</h2>
              {!showLotAnalysis && (
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => setViewMode("summary")}>
                    Summary
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => setViewMode("grouped")}>
                    By Defect Type
                  </Button>
                </div>
              )}
            </div>

            {/* Summary View */}
            {viewMode === "summary" && !selectedWafer && !showLotAnalysis && (
              <div className="grid md:grid-cols-4 gap-4 mb-8">
                <Card className="cursor-pointer hover:border-primary transition-colors" onClick={() => setViewMode("grouped")}>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between mb-2">
                      <Package className="h-8 w-8 text-primary" />
                      <span className="text-3xl font-bold">{waferAnalyses.length}</span>
                    </div>
                    <p className="text-sm text-muted-foreground">Total Wafers</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between mb-2">
                      <CheckCircle2 className="h-8 w-8 text-green-400" />
                      <span className="text-3xl font-bold text-green-400">
                        {waferAnalyses.filter(w => w.finalVerdict === "PASS").length}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground">Passed</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between mb-2">
                      <AlertTriangle className="h-8 w-8 text-red-400" />
                      <span className="text-3xl font-bold text-red-400">
                        {waferAnalyses.filter(w => w.finalVerdict === "FAIL").length}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground">Defective</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between mb-2">
                      <TrendingUp className="h-8 w-8 text-accent" />
                      <span className="text-3xl font-bold">
                        {((waferAnalyses.filter(w => w.finalVerdict === "PASS").length / waferAnalyses.length) * 100).toFixed(1)}%
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground">Yield Rate</p>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Grouped by Defect Type View */}
            {viewMode === "grouped" && !selectedWafer && (
              <div className="space-y-6 mb-8">
                {/* Defect Type Filter Buttons */}
                <div className="flex flex-wrap gap-2 mb-4">
                  <Button
                    variant={selectedDefectFilter === "all" ? "default" : "outline"}
                    onClick={() => setSelectedDefectFilter("all")}
                    size="sm"
                  >
                    All ({waferAnalyses.length})
                  </Button>
                  {Array.from(new Set(waferAnalyses.map(w => w.detectedPattern))).map(pattern => (
                    <Button
                      key={pattern}
                      variant={selectedDefectFilter === pattern ? "default" : "outline"}
                      onClick={() => setSelectedDefectFilter(pattern)}
                      size="sm"
                      className={cn(
                        pattern === "None" ? "border-green-500/50" : "border-red-500/50"
                      )}
                    >
                      {pattern} ({waferAnalyses.filter(w => w.detectedPattern === pattern).length})
                    </Button>
                  ))}
                </div>

                {/* Wafer Grid */}
                <div className="grid md:grid-cols-4 lg:grid-cols-6 gap-4">
                  {waferAnalyses
                    .filter(w => selectedDefectFilter === "all" || w.detectedPattern === selectedDefectFilter)
                    .map(wafer => (
                      <Card
                        key={wafer.waferId}
                        className="cursor-pointer hover:border-primary transition-colors"
                        onClick={() => { setSelectedWafer(wafer); setViewMode("individual"); }}
                      >
                        <CardContent className="pt-4">
                          <div className="text-center">
                            <div className="w-16 h-16 mx-auto mb-2 rounded-full bg-secondary flex items-center justify-center">
                              <span className="text-2xl">💿</span>
                            </div>
                            <p className="font-mono text-xs mb-1">{wafer.fileName}</p>
                            <Badge
                              className={cn(
                                wafer.finalVerdict === "PASS"
                                  ? "bg-green-500/20 text-green-400"
                                  : "bg-red-500/20 text-red-400"
                              )}
                            >
                              {wafer.detectedPattern}
                            </Badge>
                            <p className="text-xs text-muted-foreground mt-1">
                              {wafer.confidence.toFixed(1)}% conf
                            </p>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                </div>
              </div>
            )}

            {/* Individual Wafer View */}
            {selectedWafer && (
              <div className="space-y-6 mb-8">
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={() => { setSelectedWafer(null); setViewMode("grouped"); }}
                  >
                    <ChevronLeft className="mr-2 h-4 w-4" />
                    Back to All Wafers
                  </Button>
                  <Button
                    variant="default"
                    onClick={() => generateReport(selectedWafer)}
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Download Report
                  </Button>
                </div>

                <Card className="border-2">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-2xl font-mono">{selectedWafer.fileName}</CardTitle>
                        <CardDescription>ID: {selectedWafer.waferId} | Model: {selectedWafer.modelUsed || "k_cross_CNN.pt"} | Device: {selectedWafer.deviceUsed || "cpu"}</CardDescription>
                      </div>
                      <div className="flex items-center gap-4">
                        <Badge className={cn(
                          selectedWafer.severity === "High" ? "bg-red-500/20 text-red-400" :
                            selectedWafer.severity === "Medium" ? "bg-yellow-500/20 text-yellow-400" :
                              "bg-green-500/20 text-green-400"
                        )}>
                          {selectedWafer.severity} Severity
                        </Badge>
                        <div
                          className={cn(
                            "px-6 py-3 rounded-lg font-bold text-lg",
                            selectedWafer.finalVerdict === "PASS"
                              ? "bg-green-500/20 text-green-400 border-2 border-green-500/50"
                              : "bg-red-500/20 text-red-400 border-2 border-red-500/50"
                          )}
                        >
                          {selectedWafer.finalVerdict}
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-6">

                    {/* Pipeline Steps Overview */}
                    <div className="grid md:grid-cols-4 gap-4">
                      {/* Ingestion Card */}
                      <Card className="bg-secondary/20">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-sm flex items-center gap-2">
                            <Upload className="h-4 w-4" />
                            Ingestion Agent
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="text-xs space-y-1">
                          {selectedWafer.ingestionDetails ? (
                            <>
                              <p>📐 Shape: {selectedWafer.ingestionDetails.waferMapShape?.join('×')}</p>
                              <p>📊 Tensor: {selectedWafer.ingestionDetails.tensorShape?.join('×')}</p>
                              <p className="text-muted-foreground">Non-wafer: {selectedWafer.ingestionDetails.nonWaferCount}</p>
                              <p className="text-green-400">Normal: {selectedWafer.ingestionDetails.normalCount}</p>
                              <p className="text-red-400">Defect: {selectedWafer.ingestionDetails.defectCount}</p>
                            </>
                          ) : (
                            <p className="text-muted-foreground">Loading...</p>
                          )}
                        </CardContent>
                      </Card>

                      {/* Analysis Card */}
                      <Card className="bg-secondary/20">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-sm flex items-center gap-2">
                            <Brain className="h-4 w-4" />
                            Analysis Agent
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="text-xs space-y-1">
                          {selectedWafer.analysisDetails ? (
                            <>
                              <p>🎯 Consistency: {(selectedWafer.analysisDetails.consistencyScore * 100).toFixed(0)}%</p>
                              <p className={selectedWafer.analysisDetails.recommendation === "PASS" ? "text-green-400" : "text-yellow-400"}>
                                📋 {selectedWafer.analysisDetails.recommendation}
                              </p>
                              <p className="text-muted-foreground">
                                Issues: {selectedWafer.analysisDetails.issuesFound?.length || 0}
                              </p>
                            </>
                          ) : (
                            <p className="text-muted-foreground">Loading...</p>
                          )}
                        </CardContent>
                      </Card>

                      {/* Validation Card */}
                      <Card className="bg-secondary/20">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-sm flex items-center gap-2">
                            <CheckCircle2 className="h-4 w-4" />
                            Validation Agent
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="text-xs space-y-1">
                          {selectedWafer.validationDetails ? (
                            <>
                              <p className={selectedWafer.validationDetails.passed ? "text-green-400" : "text-red-400"}>
                                {selectedWafer.validationDetails.passed ? "✅ PASSED" : "❌ FAILED"}
                              </p>
                              <p>Attempt: {selectedWafer.validationDetails.attempts}/{selectedWafer.validationDetails.maxAttempts}</p>
                              {selectedWafer.validationDetails.criteriaChecks?.map((check, i) => (
                                <p key={i} className={check.passed ? "text-green-400" : "text-red-400"}>
                                  {check.passed ? "✓" : "✗"} {check.name}
                                </p>
                              ))}
                            </>
                          ) : (
                            <p className="text-muted-foreground">Loading...</p>
                          )}
                        </CardContent>
                      </Card>

                      {/* Trigger Card */}
                      <Card className="bg-secondary/20">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-sm flex items-center gap-2">
                            <AlertTriangle className="h-4 w-4" />
                            Trigger Agent
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="text-xs space-y-1">
                          {selectedWafer.triggerAction ? (
                            <>
                              <p className={selectedWafer.triggerAction.alertSent ? "text-red-400" : "text-green-400"}>
                                {selectedWafer.triggerAction.alertSent ? "🚨 ALERT SENT" : "✅ No Alert"}
                              </p>
                              {selectedWafer.triggerAction.alertSent && (
                                <>
                                  <p className="text-muted-foreground truncate" title={selectedWafer.triggerAction.recipient}>
                                    📧 {selectedWafer.triggerAction.recipient}
                                  </p>
                                  {selectedWafer.triggerAction.actions?.slice(0, 2).map((action, i) => (
                                    <p key={i} className="text-yellow-400">► {action}</p>
                                  ))}
                                </>
                              )}
                            </>
                          ) : (
                            <p className="text-muted-foreground">Loading...</p>
                          )}
                        </CardContent>
                      </Card>
                    </div>

                    {/* Probability Distribution with Visual Bars */}
                    <div>
                      <h4 className="font-semibold mb-3 flex items-center gap-2">
                        <Activity className="h-4 w-4" />
                        Full Probability Distribution
                      </h4>
                      <div className="grid md:grid-cols-3 gap-2">
                        {Object.entries(selectedWafer.fullProbabilityDistribution)
                          .sort(([, a], [, b]) => b - a)
                          .map(([pattern, prob]) => (
                            <div key={pattern} className={cn(
                              "flex items-center gap-2 p-2 rounded border",
                              pattern === selectedWafer.detectedPattern
                                ? "bg-primary/20 border-primary"
                                : "bg-secondary/30 border-border"
                            )}>
                              <span className="text-sm font-mono w-24">{pattern}</span>
                              <div className="flex-1 bg-secondary rounded-full h-3">
                                <div
                                  className={cn(
                                    "h-3 rounded-full transition-all",
                                    pattern === selectedWafer.detectedPattern ? "bg-primary" :
                                      prob > 10 ? "bg-yellow-500/50" : "bg-muted-foreground/30"
                                  )}
                                  style={{ width: `${Math.min(prob, 100)}%` }}
                                />
                              </div>
                              <span className={cn(
                                "text-xs font-mono w-16 text-right font-bold",
                                pattern === selectedWafer.detectedPattern && "text-primary"
                              )}>
                                {prob.toFixed(2)}%
                              </span>
                            </div>
                          ))}
                      </div>
                    </div>

                    {/* Agent Results Grid */}
                    <div>
                      <h4 className="font-semibold mb-3 flex items-center gap-2">
                        <Cpu className="h-4 w-4" />
                        Agent Analysis Details
                      </h4>
                      <div className="grid md:grid-cols-3 gap-4">
                        {selectedWafer.agentResults.map((agent, idx) => (
                          <div key={idx} className="p-4 bg-secondary/30 rounded-lg border border-border">
                            <div className="flex items-center gap-2 mb-3">
                              {agent.icon}
                              <div>
                                <p className="font-semibold text-sm">{agent.name}</p>
                                <p className="text-xs text-muted-foreground">{agent.model}</p>
                              </div>
                            </div>
                            <div className="flex items-center gap-2 mb-2">
                              <Badge className={cn(
                                agent.confidence >= 80 ? "bg-green-500/20 text-green-400" :
                                  agent.confidence >= 60 ? "bg-yellow-500/20 text-yellow-400" :
                                    "bg-red-500/20 text-red-400"
                              )}>
                                {agent.topPattern} - {agent.confidence.toFixed(1)}%
                              </Badge>
                            </div>
                            <p className="text-sm mb-3 text-muted-foreground">{agent.description}</p>
                            {agent.qualityFlag && (
                              <p className="text-xs bg-yellow-500/20 text-yellow-400 p-2 rounded mb-2">{agent.qualityFlag}</p>
                            )}
                            {agent.rootCauses.length > 0 && (
                              <div className="mt-2">
                                <p className="text-xs font-semibold mb-1">🔍 Root Causes:</p>
                                <ul className="text-xs space-y-1">
                                  {agent.rootCauses.map((cause, i) => (
                                    <li key={i} className="text-yellow-400">• {cause}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            {agent.actionSuggestions.length > 0 && (
                              <div className="mt-2">
                                <p className="text-xs font-semibold mb-1">🛠️ Actions:</p>
                                <ul className="text-xs space-y-1">
                                  {agent.actionSuggestions.map((action, i) => (
                                    <li key={i} className="text-green-400">• {action}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Full Explanation */}
                    {selectedWafer.explanation && (
                      <div className="p-4 bg-gradient-to-r from-secondary/50 to-secondary/20 rounded-lg border border-border">
                        <h4 className="font-semibold mb-3 flex items-center gap-2">
                          <FileText className="h-4 w-4" />
                          Detailed Explanation Report
                        </h4>
                        <pre className="text-sm text-muted-foreground whitespace-pre-wrap font-mono bg-background/50 p-4 rounded">
                          {selectedWafer.explanation}
                        </pre>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}

