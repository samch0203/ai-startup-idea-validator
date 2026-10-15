import { INDUSTRIES } from "../config.js";

export const LIMITS = {
  nameMin: 2,
  nameMax: 80,
  descriptionMin: 30,
  descriptionMax: 1000,
  customersMin: 3,
  customersMax: 300,
  detailsMax: 1000,
  optionalShortMax: 100,
};

export const EMPTY_FORM = {
  name: "",
  description: "",
  industry: "",
  target_customers: "",
  location: "",
  budget: "",
  details: "",
};

// Returns an object like { description: "message" }. Empty object = valid.
export function validateIdea(form) {
  const errors = {};
  const name = form.name.trim();
  const description = form.description.trim();
  const customers = form.target_customers.trim();
  const details = form.details.trim();

  if (!name) {
    errors.name = "Please enter your startup's name.";
  } else if (name.length < LIMITS.nameMin) {
    errors.name = `The name needs at least ${LIMITS.nameMin} characters.`;
  } else if (name.length > LIMITS.nameMax) {
    errors.name = `Keep the name under ${LIMITS.nameMax} characters.`;
  }

  if (!description) {
    errors.description = "Please describe your startup idea.";
  } else if (description.length < LIMITS.descriptionMin) {
    errors.description = `Add a little more detail (at least ${LIMITS.descriptionMin} characters).`;
  } else if (description.length > LIMITS.descriptionMax) {
    errors.description = `Keep it under ${LIMITS.descriptionMax} characters.`;
  }

  if (!form.industry) {
    errors.industry = "Please choose an industry.";
  } else if (!INDUSTRIES.includes(form.industry)) {
    errors.industry = "Please choose an industry from the list.";
  }

  if (!customers) {
    errors.target_customers = "Tell us who this is for.";
  } else if (customers.length < LIMITS.customersMin) {
    errors.target_customers = "Please be a bit more specific.";
  } else if (customers.length > LIMITS.customersMax) {
    errors.target_customers = `Keep it under ${LIMITS.customersMax} characters.`;
  }

  if (form.location.trim().length > LIMITS.optionalShortMax) {
    errors.location = `Keep it under ${LIMITS.optionalShortMax} characters.`;
  }
  if (form.budget.trim().length > LIMITS.optionalShortMax) {
    errors.budget = `Keep it under ${LIMITS.optionalShortMax} characters.`;
  }
  if (details.length > LIMITS.detailsMax) {
    errors.details = `Keep it under ${LIMITS.detailsMax} characters.`;
  }

  return errors;
}
