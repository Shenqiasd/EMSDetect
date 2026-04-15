# Storage Report Platform Design

**Date:** 2026-04-15

**Context**

The current storage-identification project can already ingest result data, score day-level storage signals, roll results to meter and enterprise level, and generate delivery-ready CSV artifacts for a real project run. The next step is to present those results to customers through a reusable web product rather than through raw CSV files.

This document defines the first product design for a reusable storage identification report platform. The platform is intended for two usage modes:

1. Enesource staff presenting results live to customers
2. Customers opening the platform later to review conclusions and inspect evidence on their own

The agreed constraints for the first version are:

1. The product should be a reusable report platform, not a one-off project page
2. It will be deployed on Railway
3. It will be accessed remotely
4. No login or permission system is required in v1
5. The default experience should lead with report conclusions, then allow drill-down into details

## Product Goal

Build a lightweight report platform that makes storage-identification project outputs understandable, credible, and reviewable.

The platform should let a customer:

1. Understand the overall project conclusion within 3 minutes
2. See why the result is credible without reading raw data files
3. Find a specific enterprise account and inspect the underlying evidence within 10 minutes

The platform should let Enesource:

1. Reuse the same product structure across multiple projects
2. Publish a new project by preparing a standard project dataset
3. Use the same platform both for live presentation and customer self-service review

## Non-Goals

The first version should not attempt to be a full analytics platform.

Excluded from v1:

1. Authentication and role-based access control
2. Customer-side file upload and online analysis runs
3. Online rule tuning or model parameter editing
4. Full BI-style custom dashboards
5. Heavy day-curve playback tooling
6. Project administration workflows beyond simple project registration

## Primary User Scenarios

### Scenario 1: Live customer presentation

An Enesource analyst opens a project report and walks a customer through:

1. Project scope and data period
2. Overall identification result
3. High-confidence storage enterprises
4. Review recommendations
5. One or two representative enterprise examples

The product must support a clear narrative and clean visual hierarchy.

### Scenario 2: Customer self-review after the meeting

A customer opens the same project URL later and:

1. Reviews the top conclusions again
2. Searches for a specific enterprise account
3. Opens the enterprise detail page
4. Checks which meters and dates support the conclusion
5. Understands whether the result is high confidence or still needs manual review

The product must support evidence drill-down without requiring technical model knowledge.

### Scenario 3: Reuse for future projects

Enesource prepares a new project dataset and publishes a new project report without redesigning the site. The platform must therefore have a project abstraction rather than hard-coded single-project content.

## Product Principles

### 1. Conclusions first

The first screen should answer:

1. What was analyzed
2. What was found
3. What should the customer focus on next

### 2. Evidence must be explainable

The platform should not expose only raw model labels and scores. It must translate results into business-readable explanations using:

1. Enterprise-level conclusion
2. Key supporting meter accounts
3. Key evidence dates
4. Matched rule patterns
5. Suggested next action

### 3. Reusable by project

Every page should be project-scoped. The same page templates should work for different result sets.

### 4. Light operational complexity

The first version should minimize operational burden. Static project artifacts or simple structured project data are preferred over a complex backend control plane.

## Information Architecture

The v1 platform should contain five pages.

### 1. Project List Page

Purpose:
Show all available storage-identification report projects.

Key content:

1. Project name
2. Customer name or project alias if available
3. Data period
4. Enterprise count
5. High-confidence storage count
6. Manual review count
7. Short result summary
8. Link to open the project report

### 2. Project Overview Page

Purpose:
Serve as the default landing page for a project and summarize the project results.

Key content:

1. Project header
2. Data period and basic scope
3. KPI cards
4. Distribution chart or summary blocks for result categories
5. Key conclusion summary
6. High-confidence shortlist preview
7. Manual-review shortlist preview
8. Typical sample entry point
9. Method explanation entry point

This page is optimized for presentation and executive understanding.

### 3. Identification Results Page

Purpose:
Provide a searchable and sortable enterprise result list.

Key content:

1. Tab or segmented control for:
   - High-confidence storage
   - Manual review
   - Optional all enterprises
2. Search by enterprise account number
3. Filters for:
   - Business conclusion
   - Manual review tier
   - Score range
   - Meter count
4. Sorting by:
   - Enterprise score
   - Review priority
   - Meter count
5. Detail entry for each row

This page is optimized for business operation and account review.

### 4. Enterprise Detail Page

Purpose:
Explain a single enterprise conclusion clearly.

Key content:

1. Enterprise summary card
2. Business conclusion and model label
3. Enterprise score and ranking
4. Suggested action
5. Explanation block: why this enterprise was judged this way
6. Top supporting meters
7. Evidence dates
8. Matched rules
9. Meter comparison
10. Optional simple evidence timeline

This is the core trust-building page.

### 5. Method Explanation Page

Purpose:
Explain the storage-identification methodology in business language.

Key content:

1. What data was used
2. What the platform detects
3. How day-level, meter-level, and enterprise-level judgment works
4. What the labels mean
5. Why high-confidence results are credible
6. Why manual review is still needed for some enterprises
7. Typical example

This page supports both sales credibility and customer review.

## Navigation Model

Recommended navigation flow:

1. Project list
2. Project overview
3. Results list
4. Enterprise detail
5. Method explanation

Within a project:

1. The project overview page is the default landing page
2. Enterprise detail pages should be reachable from both overview previews and result tables
3. Method explanation should always remain accessible from the top navigation

## Page-Level Functional Design

## Project List Page

### User objective

Pick the correct project quickly.

### Components

1. Project cards or a compact table
2. Search by project name
3. Optional sort by date

### Required project metadata

1. Project identifier
2. Project display name
3. Data start date
4. Data end date
5. Enterprise count
6. High-confidence count
7. Manual review count
8. Last updated time

## Project Overview Page

### User objective

Understand the overall project result and next-step focus quickly.

### Components

1. Hero section
   - Project name
   - Data period
   - One-sentence summary
2. KPI cards
   - Enterprise total
   - High-confidence storage enterprises
   - Manual review enterprises
   - No-storage enterprises
3. Result composition section
   - Category distribution visual
4. Business takeaway section
   - Three or four key messages
5. Priority enterprise preview
   - Top high-confidence enterprises
6. Manual review preview
   - Top P1 review enterprises
7. Representative example block
   - One enterprise shown in narrative form
8. Links to detail pages

### Example high-level summary copy structure

1. "This project analyzed X enterprises over Y days"
2. "Z enterprises were identified as high-confidence storage targets"
3. "A additional enterprises should be manually reviewed"
4. "The strongest evidence comes from repeated charge/discharge pair patterns across key meters and dates"

## Identification Results Page

### User objective

Find target enterprises and compare them efficiently.

### Components

1. Search input
2. Tab filters
3. Review tier filters
4. Score filters
5. Enterprise result table

### Recommended columns

1. Enterprise account number
2. Business conclusion
3. Model label
4. Enterprise score
5. Review priority or review tier
6. Meter count
7. Strong-signal meter count
8. Top meter
9. Top evidence dates
10. Review reason
11. Detail link

### Behavior

1. Default tab should show conclusion-oriented groups, not raw full data
2. High-confidence and manual-review tabs should be easy to scan
3. The table should not overload the user with all top1-top3 fields at once

## Enterprise Detail Page

### User objective

Understand a single enterprise decision with confidence.

### Page structure

#### A. Decision summary

Show:

1. Enterprise account number
2. Business conclusion
3. Model label
4. Enterprise score
5. Ranking or review tier
6. Suggested next action

#### B. Why this result

Translate the evidence into business language. For example:

1. Whether the enterprise has one or more strong-signal meters
2. Whether signals repeat across many days
3. Whether the top rule pattern is charge/discharge pair
4. Whether multiple meters support the conclusion

#### C. Supporting meters

Display top1 and top2 meters as cards with:

1. Meter number
2. Meter label
3. Meter score
4. Usable day count
5. Positive day ratio
6. Strong positive day count
7. Evidence dates
8. Matched rules

#### D. Evidence dates and rules

Display the key evidence dates and rules in a compact timeline or chip list.

#### E. Recommended action

Provide a business-oriented recommendation based on conclusion type:

1. High confidence: prioritize commercial follow-up or customer confirmation
2. Manual review: review load curves and business context
3. No storage: low follow-up priority unless external business evidence suggests otherwise

## Method Explanation Page

### User objective

Understand the methodology without reading technical implementation code.

### Sections

1. Input data description
2. Detection logic in three stages
   - Day level
   - Meter level
   - Enterprise level
3. Label definitions
4. Why repeated behavior matters more than one-off anomalies
5. What makes a result high confidence
6. Why some enterprises remain in manual review
7. Typical high-confidence example

### Tone

The tone should be explanatory and credible, not overly academic.

## Data Model Design

The platform should be project-driven.

### Project entity

Recommended fields:

1. `project_id`
2. `project_name`
3. `customer_name` nullable
4. `data_start_date`
5. `data_end_date`
6. `enterprise_total`
7. `high_confidence_total`
8. `manual_review_total`
9. `no_storage_total`
10. `summary_text`
11. `artifact_version`

### Enterprise report entity

Recommended source:

Use `enterprise_identification_base.csv` as the canonical enterprise result source for the project, and derive UI-specific datasets from it when needed.

Recommended enterprise fields:

1. Enterprise account number
2. Business label
3. Model label
4. Enterprise score
5. Review priority
6. Meter counts
7. Strong meter counts
8. Top meter list
9. Top evidence dates
10. Top hit rules
11. Review reason
12. Top1 meter fields
13. Top2 meter fields

### Derived dataset sources

The current project already has:

1. `enterprise_identification_base.csv`
2. `enterprise_identification_high_confidence.csv`
3. `enterprise_identification_manual_review.csv`
4. Chinese delivery versions

Recommended product data flow:

1. Standardize input project artifacts into a structured project folder
2. Load enterprise base data
3. Derive summary KPI values
4. Populate project overview and results pages

## Data Preparation Strategy

For v1, avoid a heavy ingestion pipeline inside the web app.

Recommended strategy:

1. Prepare a standard project manifest file plus result CSV files
2. At deploy or build time, load these project files
3. Expose a unified read model to the frontend

This keeps the product simple and stable while allowing multiple projects.

## Visual and Content Direction

The visual style should sit between a consulting report and a modern data product.

### Desired feel

1. Credible
2. Professional
3. Clean
4. Structured
5. Suitable for presentation screenshots

### Avoid

1. BI dashboard clutter
2. Generic admin template aesthetics
3. Flat tables with no narrative hierarchy

### Recommended tone

1. Lead with conclusions
2. Use restrained color coding for categories
3. Use score and category emphasis carefully
4. Keep explanatory copy concise and business-oriented

## MVP Scope

The first release should include:

1. Multi-project support
2. Project list page
3. Project overview page
4. Enterprise results page
5. Enterprise detail page
6. Method explanation page
7. Enterprise search
8. Basic filtering and sorting
9. Project data loading from standard artifacts
10. Railway deployment

## Future Iterations

Potential v2 and v3 additions:

1. Day-level evidence chart visualization
2. CSV export from UI
3. Better project management tooling
4. Customer annotations on enterprises
5. Authentication and project access control
6. Online data upload
7. Deeper evidence drill-down to day curve graphics

## Recommendation Summary

The recommended first version is a lightweight reusable report platform with:

1. Conclusion-first project overview
2. Searchable enterprise result pages
3. Evidence-based enterprise detail pages
4. Business-readable method explanation
5. Simple project-scoped data loading

This scope is large enough to feel like a real product and small enough to ship quickly on top of the existing storage-identification outputs.
