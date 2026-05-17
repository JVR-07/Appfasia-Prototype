export type ActivityType = "naming" | "repetition" | "match" | "constructor";

export interface ActivityInstance {
  id: string;
  type: "naming" | "repetition" | "match" | "constructor";
  title: string;
  subtitle: string;
  targetWord: string;
  imageUrl?: string;
  audioUrl?: string;
  options?: { id: string; label: string; imageUrl?: string }[];
}

export interface ActivityResult {
  activityId: string;
  isCorrect: boolean;
  timeTakenMs: number;
  attempts: number;
  idSeleccionado?: string;
}
