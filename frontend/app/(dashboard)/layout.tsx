import { AppSidebar } from "@/components/layout/AppSidebar";

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <>
            <AppSidebar showBackButton={true} />
            {children}
        </>
    );
}
