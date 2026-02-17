"use client";

import { Bell, Search, User } from "lucide-react";

interface HeaderProps {
  title?: string;
}

export function Header({ title }: HeaderProps) {
  return (
    <header className="flex h-16 items-center justify-between border-b border-gray-200 bg-white px-6">
      <div className="flex items-center gap-4">
        {title && <h1 className="text-xl font-semibold text-gray-900">{title}</h1>}
      </div>

      <div className="flex items-center gap-3">
        {/* Search */}
        <button className="rounded-lg p-2 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600">
          <Search className="h-5 w-5" />
        </button>

        {/* Notifications */}
        <button className="relative rounded-lg p-2 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600">
          <Bell className="h-5 w-5" />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-red-500" />
        </button>

        {/* User avatar */}
        <button className="flex items-center gap-2 rounded-lg p-1.5 transition-colors hover:bg-gray-100">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-aiden-100">
            <User className="h-4 w-4 text-aiden-600" />
          </div>
        </button>
      </div>
    </header>
  );
}
