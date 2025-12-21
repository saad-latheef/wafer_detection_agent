"use client";

import HeroSection from "@/components/hero/HeroSection";
import ProblemSection from "@/components/sections/ProblemSection";
import WorkflowSection from "@/components/sections/WorkflowSection";
import AutomationSection from "@/components/sections/AutomationSection";
import AgenticSection from "@/components/sections/AgenticSection";
import LiveDemoSection from "@/components/sections/LiveDemoSection";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  return (
    <div className="min-h-screen">
      <HeroSection />
      <ProblemSection />
      <WorkflowSection />
      <AutomationSection />
      <AgenticSection />
      <LiveDemoSection onStartAnalysis={() => router.push("/analysis")} />
    </div>
  );
}
