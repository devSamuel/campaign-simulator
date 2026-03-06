"use client";

import { useState } from "react";
import { StepNav } from "./StepNav";
import { StepInfo } from "./StepInfo";
import { StepCreativities } from "./StepCreativities";
import { StepAudience } from "./StepAudience";
import { StepRule } from "./StepRule";
import { StepSimulate } from "./StepSimulate";
import type { Campaign } from "@/lib/types";

export function CampaignBuilder({ campaign }: { campaign: Campaign }) {
  const [activeStep, setActiveStep] = useState(1);

  return (
    <div>
      <StepNav
        activeStep={activeStep}
        campaign={campaign}
        onStepChange={setActiveStep}
      />
      <div className="mt-6">
        {activeStep === 1 && <StepInfo campaign={campaign} />}
        {activeStep === 2 && <StepCreativities campaign={campaign} />}
        {activeStep === 3 && <StepAudience campaign={campaign} />}
        {activeStep === 4 && <StepRule campaign={campaign} />}
        {activeStep === 5 && <StepSimulate campaign={campaign} />}
      </div>
    </div>
  );
}
