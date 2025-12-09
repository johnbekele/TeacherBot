export interface Node {
  node_id: string;
  title: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimated_duration: number;
  prerequisites: string[];
  skills_taught: string[];
  locked: boolean;
  completion_status: 'not_started' | 'in_progress' | 'completed';
  completion_percentage: number;
}

export interface NodeContent {
  introduction: string;
  concepts: string[];
  practical_applications: string[];
}

export interface NodeDetail extends Node {
  content: NodeContent;
  exercises: ExerciseSummary[];
}

export interface ExerciseSummary {
  exercise_id: string;
  title: string;
  difficulty: string;
  completed: boolean;
}

export interface NodeProgress {
  status: 'not_started' | 'in_progress' | 'completed';
  completion_percentage: number;
  exercises_completed: number;
  exercises_total: number;
}
