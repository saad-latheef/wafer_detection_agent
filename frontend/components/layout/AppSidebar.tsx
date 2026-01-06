"use client";

import { useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
    Activity,
    ArrowLeft,
    ChevronLeft,
    Cpu,
    FileText,
    TrendingUp,
} from "lucide-react";

interface AppSidebarProps {
    showBackButton?: boolean;
    currentPage?: "dashboard" | "analytics" | "spc" | "rca" | "parameters" | "copilot" | "history" | "config";
}

export function AppSidebar({ showBackButton = false, currentPage }: AppSidebarProps) {
    const router = useRouter();
    const pathname = usePathname();
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

    const activePage = currentPage || (() => {
        if (pathname.startsWith("/analysis")) return "dashboard";
        if (pathname.startsWith("/analytics")) return "analytics";
        if (pathname.startsWith("/spc")) return "spc";
        if (pathname.startsWith("/rca")) return "rca";
        if (pathname.startsWith("/parameters")) return "parameters";
        if (pathname.startsWith("/copilot")) return "copilot";
        if (pathname.startsWith("/history")) return "history";
        if (pathname.startsWith("/notifications")) return "config";
        return "dashboard";
    })();

    return (
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
                    {showBackButton && (
                        <Button
                            variant="ghost"
                            onClick={() => router.push("/")}
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
                        variant={activePage === "dashboard" ? "secondary" : "ghost"}
                        onClick={() => router.push("/analysis")}
                        className={cn(
                            "w-full",
                            activePage !== "dashboard" && "text-sidebar-foreground hover:text-sidebar-foreground hover:bg-sidebar-accent",
                            sidebarCollapsed ? "justify-center px-0" : "justify-start"
                        )}
                    >
                        <Activity className={cn("h-4 w-4", !sidebarCollapsed && "mr-2")} />
                        {!sidebarCollapsed && "Dashboard"}
                    </Button>
                    <Button
                        variant={activePage === "analytics" ? "secondary" : "ghost"}
                        onClick={() => router.push("/analytics")}
                        className={cn(
                            "w-full",
                            activePage !== "analytics" && "text-sidebar-foreground hover:text-sidebar-foreground hover:bg-sidebar-accent",
                            sidebarCollapsed ? "justify-center px-0" : "justify-start",
                        )}
                    >
                        <TrendingUp className={cn("h-4 w-4", !sidebarCollapsed && "mr-2")} />
                        {!sidebarCollapsed && "Analytics"}
                    </Button>
                    <Button
                        variant={activePage === "spc" ? "secondary" : "ghost"}
                        onClick={() => router.push("/spc")}
                        className={cn(
                            "w-full",
                            activePage !== "spc" && "text-sidebar-foreground hover:text-sidebar-foreground hover:bg-sidebar-accent",
                            sidebarCollapsed ? "justify-center px-0" : "justify-start",
                        )}
                    >
                        <Activity className={cn("h-4 w-4", !sidebarCollapsed && "mr-2")} />
                        {!sidebarCollapsed && "SPC Charts"}
                    </Button>
                    <Button
                        variant={activePage === "rca" ? "secondary" : "ghost"}
                        onClick={() => router.push("/rca")}
                        className={cn(
                            "w-full",
                            activePage !== "rca" && "text-sidebar-foreground hover:text-sidebar-foreground hover:bg-sidebar-accent",
                            sidebarCollapsed ? "justify-center px-0" : "justify-start",
                        )}
                    >
                        <Cpu className={cn("h-4 w-4", !sidebarCollapsed && "mr-2")} />
                        {!sidebarCollapsed && "Root Cause"}
                    </Button>
                    <Button
                        variant={activePage === "parameters" ? "secondary" : "ghost"}
                        onClick={() => router.push("/parameters")}
                        className={cn(
                            "w-full",
                            activePage !== "parameters" && "text-sidebar-foreground hover:text-sidebar-foreground hover:bg-sidebar-accent",
                            sidebarCollapsed ? "justify-center px-0" : "justify-start",
                        )}
                    >
                        <FileText className={cn("h-4 w-4", !sidebarCollapsed && "mr-2")} />
                        {!sidebarCollapsed && "Parameters"}
                    </Button>
                    <Button
                        variant={activePage === "copilot" ? "secondary" : "ghost"}
                        onClick={() => router.push("/copilot")}
                        className={cn(
                            "w-full",
                            activePage !== "copilot" && "text-sidebar-foreground hover:text-sidebar-foreground hover:bg-sidebar-accent",
                            sidebarCollapsed ? "justify-center px-0" : "justify-start",
                        )}
                    >
                        <Activity className={cn("h-4 w-4", !sidebarCollapsed && "mr-2")} />
                        {!sidebarCollapsed && "AI Copilot"}
                    </Button>
                    <Button
                        variant={activePage === "history" ? "secondary" : "ghost"}
                        onClick={() => router.push("/history")}
                        className={cn(
                            "w-full",
                            activePage !== "history" && "text-sidebar-foreground hover:text-sidebar-foreground hover:bg-sidebar-accent",
                            sidebarCollapsed ? "justify-center px-0" : "justify-start",
                        )}
                    >
                        <FileText className={cn("h-4 w-4", !sidebarCollapsed && "mr-2")} />
                        {!sidebarCollapsed && "Scan History"}
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
    );
}
