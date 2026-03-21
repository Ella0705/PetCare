export type RiskLevel = "low" | "moderate" | "high" | "urgent";

export interface FinalPetHealthReport {
  metadata: {
    species: string;
    age_years: number;
    weight_kg: number;
    sex: string;
    neutered: boolean;
  };
  owner_symptoms: string;
  intake: {
    case_summary: string;
    normalized_symptoms: string[];
    red_flag_keywords: string[];
    safety_disclaimer: string;
  };
  vision: {
    image_count: number;
    observations: { label: string; confidence: number; note: string }[];
    uncertainty_notes: string[];
  };
  risk: {
    risk_level: RiskLevel;
    risk_reasons: string[];
    urgent_red_flags: string[];
    escalation_guidance: string;
    uncertainty_statement: string;
  };
  feeding: {
    feeding_advice: string[];
    hydration_advice: string[];
    avoid_list: string[];
    monitoring_tips: string[];
  };
  non_diagnostic_notice: string;
}
