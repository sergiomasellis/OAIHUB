"use client"
import React from "react"

export default function SuspenseWrapper({
  children,
}: {
  children: React.ReactNode
}) {
  return <React.Suspense>{children}</React.Suspense>
}
