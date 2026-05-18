export type ActivityType = "naming" | "repetition" | "match" | "constructor" | "narrator" | "thinker";

export interface ActivityInstance {
  id: string;
  type: ActivityType;
  title: string;
  subtitle: string;
  targetWord: string;
  imageUrl?: string;
  audioUrl?: string;
  plantilla?: string;
  idRecurso?: string;
  idHito?: string;
  options?: { id: string; label: string; imageUrl?: string }[];
}

export interface ActivityResult {
  activityId: string;
  isCorrect: boolean;
  timeTakenMs: number;
  attempts: number;
  idSeleccionado?: string;
  audioBase64?: string;
  transcript?: string;
  plantilla?: string;
  idRecurso?: string;
  idHito?: string;
  textoEsperado?: string;
}
