export interface Exercise {
  exercise_id: string;
  title: string;
  description: string;
  prompt: string;
  starter_code: string;
  type: 'python' | 'bash' | 'terraform' | 'pulumi' | 'ansible';
  difficulty: string;
}

export interface UserProgress {
  attempts: number;
  best_score: number;
  completed: boolean;
}

export interface TestResult {
  test_id: string;
  passed: boolean;
  actual_output?: any;
  error_message?: string;
}

export interface ExerciseResult {
  submission_id: string;
  status: 'grading' | 'completed' | 'failed';
  score: number;
  passed: boolean;
  test_results: TestResult[];
  feedback: string;
  next_step: string;
  hints_available: number;
}

export interface ExerciseSubmission {
  code: string;
  language: string;
}
