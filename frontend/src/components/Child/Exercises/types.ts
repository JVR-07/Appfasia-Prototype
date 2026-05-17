export type ActivityType = "naming" | "repetition" | "match";

export interface ActivityInstance {
  id: string;
  type: ActivityType;
  title: string;
  subtitle: string;
  imageUrl?: string;
  audioUrl?: string;
  targetWord: string;
  options?: { id: string; label: string; imageUrl?: string }[];
}

export interface ActivityResult {
  activityId: string;
  isCorrect: boolean;
  timeTakenMs: number;
  attempts: number;
}
