"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Mail, Bell, AlertTriangle, CheckCircle2, Loader2, Settings2 } from "lucide-react";
import { PageTransition } from "@/components/layout/PageTransition";
import { cn } from "@/lib/utils";

interface NotificationConfig {
    enabled: boolean;
    smtp_host: string;
    smtp_port: number;
    username: string;
    password: string;
    from_email: string;
    alert_threshold: number;
    recipients: string[];
    daily_digest: boolean;
    digest_time: string;
}

export default function NotificationsPage() {
    const [config, setConfig] = useState<NotificationConfig>({
        enabled: false,
        smtp_host: "smtp.gmail.com",
        smtp_port: 587,
        username: "",
        password: "",
        from_email: "",
        alert_threshold: 15,
        recipients: [],
        daily_digest: true,
        digest_time: "08:00"
    });
    const [newEmail, setNewEmail] = useState("");
    const [saving, setSaving] = useState(false);
    const [testSending, setTestSending] = useState(false);
    const [saveStatus, setSaveStatus] = useState<"success" | "error" | null>(null);

    const handleSave = async () => {
        setSaving(true);
        try {
            const response = await fetch("http://localhost:8000/api/notifications/configure", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(config)
            });

            if (response.ok) {
                setSaveStatus("success");
            } else {
                setSaveStatus("error");
            }
        } catch (error) {
            setSaveStatus("error");
        } finally {
            setSaving(false);
            setTimeout(() => setSaveStatus(null), 3000);
        }
    };

    const sendTestEmail = async () => {
        setTestSending(true);
        try {
            await fetch("http://localhost:8000/api/notifications/test", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ recipients: config.recipients })
            });
        } catch (error) {
            console.error("Failed to send test email:", error);
        } finally {
            setTestSending(false);
        }
    };

    const addRecipient = () => {
        if (newEmail && !config.recipients.includes(newEmail)) {
            setConfig({ ...config, recipients: [...config.recipients, newEmail] });
            setNewEmail("");
        }
    };

    const removeRecipient = (email: string) => {
        setConfig({ ...config, recipients: config.recipients.filter(e => e !== email) });
    };

    return (
        <PageTransition>
            <div className={cn("transition-all duration-300", "ml-64")}>
                <div className="container mx-auto p-8">
                    {/* Header */}
                    <div className="mb-8 flex items-center justify-between">
                        <div>
                            <h1 className="text-4xl font-bold mb-2">Notification Settings</h1>
                            <p className="text-muted-foreground">Configure email alerts and daily digest reports</p>
                        </div>
                        <div className="flex items-center gap-4">
                            {saveStatus === "success" && (
                                <Badge variant="outline" className="bg-green-500/10 text-green-500 border-green-500">
                                    <CheckCircle2 className="h-3 w-3 mr-1" />
                                    Saved
                                </Badge>
                            )}
                            <Button onClick={handleSave} disabled={saving}>
                                {saving ? (
                                    <>
                                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                        Saving...
                                    </>
                                ) : (
                                    <>
                                        <Settings2 className="h-4 w-4 mr-2" />
                                        Save Configuration
                                    </>
                                )}
                            </Button>
                        </div>
                    </div>

                    <Tabs defaultValue="alerts" className="space-y-6">
                        <TabsList>
                            <TabsTrigger value="alerts">
                                <AlertTriangle className="h-4 w-4 mr-2" />
                                Alert Settings
                            </TabsTrigger>
                            <TabsTrigger value="smtp">
                                <Mail className="h-4 w-4 mr-2" />
                                SMTP Configuration
                            </TabsTrigger>
                            <TabsTrigger value="digest">
                                <Bell className="h-4 w-4 mr-2" />
                                Daily Digest
                            </TabsTrigger>
                        </TabsList>

                        {/* Alert Settings */}
                        <TabsContent value="alerts">
                            <Card>
                                <CardHeader>
                                    <CardTitle>Alert Configuration</CardTitle>
                                    <CardDescription>
                                        Configure when and to whom alerts are sent
                                    </CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-6">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <Label className="text-base">Enable Email Notifications</Label>
                                            <p className="text-sm text-muted-foreground">
                                                Send email alerts when defect thresholds are exceeded
                                            </p>
                                        </div>
                                        <Switch
                                            checked={config.enabled}
                                            onCheckedChange={(enabled) => setConfig({ ...config, enabled })}
                                        />
                                    </div>

                                    <div className="space-y-2">
                                        <Label>Defect Rate Threshold (%)</Label>
                                        <Input
                                            type="number"
                                            value={config.alert_threshold}
                                            onChange={(e) => setConfig({ ...config, alert_threshold: parseInt(e.target.value) || 0 })}
                                            className="w-32"
                                        />
                                        <p className="text-sm text-muted-foreground">
                                            Alert when defect rate exceeds this percentage
                                        </p>
                                    </div>

                                    <div className="space-y-2">
                                        <Label>Email Recipients</Label>
                                        <div className="flex gap-2">
                                            <Input
                                                type="email"
                                                placeholder="engineer@company.com"
                                                value={newEmail}
                                                onChange={(e) => setNewEmail(e.target.value)}
                                                onKeyDown={(e) => e.key === "Enter" && addRecipient()}
                                            />
                                            <Button variant="outline" onClick={addRecipient}>Add</Button>
                                        </div>
                                        <div className="flex flex-wrap gap-2 mt-2">
                                            {config.recipients.map((email) => (
                                                <Badge
                                                    key={email}
                                                    variant="secondary"
                                                    className="cursor-pointer hover:bg-destructive hover:text-destructive-foreground"
                                                    onClick={() => removeRecipient(email)}
                                                >
                                                    {email} ×
                                                </Badge>
                                            ))}
                                        </div>
                                    </div>

                                    <Button
                                        variant="outline"
                                        onClick={sendTestEmail}
                                        disabled={testSending || config.recipients.length === 0}
                                    >
                                        {testSending ? (
                                            <>
                                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                                Sending...
                                            </>
                                        ) : (
                                            <>
                                                <Mail className="h-4 w-4 mr-2" />
                                                Send Test Email
                                            </>
                                        )}
                                    </Button>
                                </CardContent>
                            </Card>
                        </TabsContent>

                        {/* SMTP Configuration */}
                        <TabsContent value="smtp">
                            <Card>
                                <CardHeader>
                                    <CardTitle>SMTP Server Configuration</CardTitle>
                                    <CardDescription>
                                        Configure your email server settings (Gmail, SendGrid, etc.)
                                    </CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div className="grid md:grid-cols-2 gap-4">
                                        <div className="space-y-2">
                                            <Label>SMTP Host</Label>
                                            <Input
                                                value={config.smtp_host}
                                                onChange={(e) => setConfig({ ...config, smtp_host: e.target.value })}
                                                placeholder="smtp.gmail.com"
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label>SMTP Port</Label>
                                            <Input
                                                type="number"
                                                value={config.smtp_port}
                                                onChange={(e) => setConfig({ ...config, smtp_port: parseInt(e.target.value) || 587 })}
                                            />
                                        </div>
                                    </div>
                                    <div className="grid md:grid-cols-2 gap-4">
                                        <div className="space-y-2">
                                            <Label>Username</Label>
                                            <Input
                                                value={config.username}
                                                onChange={(e) => setConfig({ ...config, username: e.target.value })}
                                                placeholder="your-email@gmail.com"
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label>Password / App Password</Label>
                                            <Input
                                                type="password"
                                                value={config.password}
                                                onChange={(e) => setConfig({ ...config, password: e.target.value })}
                                                placeholder="••••••••"
                                            />
                                        </div>
                                    </div>
                                    <div className="space-y-2">
                                        <Label>From Email Address</Label>
                                        <Input
                                            value={config.from_email}
                                            onChange={(e) => setConfig({ ...config, from_email: e.target.value })}
                                            placeholder="alerts@yourcompany.com"
                                        />
                                    </div>
                                </CardContent>
                            </Card>
                        </TabsContent>

                        {/* Daily Digest */}
                        <TabsContent value="digest">
                            <Card>
                                <CardHeader>
                                    <CardTitle>Daily Digest Settings</CardTitle>
                                    <CardDescription>
                                        Receive a daily summary of fab performance
                                    </CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-6">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <Label className="text-base">Enable Daily Digest</Label>
                                            <p className="text-sm text-muted-foreground">
                                                Receive a summary email every morning
                                            </p>
                                        </div>
                                        <Switch
                                            checked={config.daily_digest}
                                            onCheckedChange={(daily_digest) => setConfig({ ...config, daily_digest })}
                                        />
                                    </div>

                                    <div className="space-y-2">
                                        <Label>Send Time</Label>
                                        <Input
                                            type="time"
                                            value={config.digest_time}
                                            onChange={(e) => setConfig({ ...config, digest_time: e.target.value })}
                                            className="w-32"
                                        />
                                        <p className="text-sm text-muted-foreground">
                                            Daily digest will be sent at this time (local timezone)
                                        </p>
                                    </div>

                                    <div className="p-4 bg-muted rounded-lg">
                                        <p className="text-sm font-medium mb-2">Digest includes:</p>
                                        <ul className="text-sm text-muted-foreground space-y-1">
                                            <li>✓ Overall yield rate</li>
                                            <li>✓ Total wafers processed</li>
                                            <li>✓ Top defect patterns</li>
                                            <li>✓ Tool performance summary</li>
                                            <li>✓ SPC violations (if any)</li>
                                        </ul>
                                    </div>
                                </CardContent>
                            </Card>
                        </TabsContent>
                    </Tabs>
                </div>
            </div>
        </PageTransition>
    );
}
