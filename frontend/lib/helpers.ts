export function getErrorMessage(error: any): string {
  const detail = error?.response?.data?.detail;

  if (!detail) return "Something went wrong";

  // Plain string error
  if (typeof detail === "string") return detail;

  // FastAPI validation error array
  if (Array.isArray(detail)) {
    return detail.map((e: any) => e.msg).join(", ");
  }

  return "Something went wrong";
}