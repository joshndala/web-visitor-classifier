export interface AnalysisQuestion {
    question: string;
    options: string[];
  }
  
  export interface AnalysisResponse {
    content: {
      title: string;
      meta_description: string;
      main_content: string;
      headings: Array<{ text: string }>;
    };
    questions: AnalysisQuestion;
  }