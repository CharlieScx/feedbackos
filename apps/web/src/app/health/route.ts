export function GET(): Response {
  return Response.json(
    { service: "feedbackos-web", status: "ok" },
    { headers: { "Cache-Control": "no-store" } },
  );
}
