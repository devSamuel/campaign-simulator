import { clsx } from "clsx";
import type { ReactNode } from "react";

type BadgeVariant = "gray" | "green" | "yellow" | "blue" | "red";

const variantClasses: Record<BadgeVariant, string> = {
  gray: "bg-gray-100 text-gray-700",
  green: "bg-green-100 text-green-700",
  yellow: "bg-yellow-100 text-yellow-700",
  blue: "bg-blue-100 text-blue-700",
  red: "bg-red-100 text-red-700",
};

export function Badge({
  children,
  variant,
}: {
  children: ReactNode;
  variant: BadgeVariant;
}) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        variantClasses[variant],
      )}
    >
      {children}
    </span>
  );
}
