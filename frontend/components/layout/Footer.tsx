import Link from "next/link";
import { Cpu } from "lucide-react";

export default function Footer() {
    return (
        <footer className="bg-background-darker border-t border-white/10">
            <div className="max-w-7xl mx-auto px-6 py-8">
                <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                    {/* Logo and Copyright */}
                    <div className="flex items-center gap-2">
                        <div className="flex items-center justify-between">
                            <p className="text-gray-500 text-sm">
                                © 2024 AgenticWafer. All rights reserved.
                            </p>
                        </div>
                    </div>

                    {/* Links */}
                    <div className="flex items-center gap-6 text-sm">
                        <Link href="#" className="text-text-secondary hover:text-text-primary transition">
                            Privacy Policy
                        </Link>
                        <Link href="#" className="text-text-secondary hover:text-text-primary transition">
                            Terms of Service
                        </Link>
                        <Link href="#" className="text-text-secondary hover:text-text-primary transition">
                            Contact Support
                        </Link>
                    </div>
                </div>
            </div>
        </footer>
    );
}
