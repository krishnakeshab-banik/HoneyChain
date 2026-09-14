export function dayPart() {
  const hour = new Date().getHours();
  if (hour < 12) {
    return "Good morning";
  }
  if (hour < 17) {
    return "Good afternoon";
  }
  return "Good evening";
}

export function welcomeLine(name, detail) {
  const who = name || "there";
  return detail ? `${dayPart()}, ${who} — ${detail}` : `${dayPart()}, ${who}`;
}
