# Zugzwang
When every move is a **wrong move**;

# File Structure
```bash
  .
  ├── AGENTS.md
  ├── CLAUDE.md
  ├── README.md
  ├── api
  ├── app
  │   ├── favicon.ico
  │   ├── globals.css
  │   ├── layout.tsx
  │   └── page.tsx
  ├── docs
  ├── eslint.config.mjs
  ├── lib
  ├── models
  ├── next.config.ts
  ├── package-lock.json
  ├── package.json
  ├── postcss.config.mjs
  ├── public
  │   ├── file.svg
  │   ├── globe.svg
  │   ├── next.svg
  │   ├── vercel.svg
  │   └── window.svg
  ├── schema
  ├── src
  └── tsconfig.json
```

## Configuration Files
All configuration files which are critical to production, are to be placed within the config directory
and is advised not to be included in any commits under any circumstances, those files are expected to
be kept confidential and should only be transferred to personnel through secure channels only.

Any exposure to the configuration files is advised to be notified to the team immediately so as to
rotate the exposed keys and configurations.

## API Directory
The API Directory holds the server components of the web interface effectively providing the backend
facilities and functionalities to the interface. The file structure should follow a version managed
route collection, i.e, routes are to be separated and categorised as per application version.

In order to facilitate, seamless development when new versions are parallely being developed.

## Documentation
Documentation should be followed for all kinds of changes in the application, any major change should
be recorded and accounted for. Each and every feature within the app (modules & integrations) are
required to be documented following the format of documentation by the respective developer(s) who
has taken part in the implementation of the said.

Constraints to be followed for all technical documentations:
- All visual representations should use either svg images or mermaid/d2 diagrams.
- When using d2/mermaid diagrams, use the apropriate diagram type that suits the scenario
- Expected file format is markdown (.md)
- Necessary classification of documents are to be done as per requirement (sorting documents by dirs)
- Architecture decisions are to be recorded and noted proeprly with every change that affects future
  development of the interface.
- Proper updation timestamps are to be included in the header of documentation files
  Format:
  ```markdown
    ## Developer: <name>
    ## Last Updated: <date>
    ## [Feature|Decision-<n>|Bugfix-<n>]
    ## <Short description for the above>
  ```

## Models
All HTTP Models should comply with industry standard requests, and should follow OpenAPI documentation
format in order to provide flexibility and understandability of the code and for the ease of integration
into different documentation and development frameworks.

For the development and designing of HTTP models, developers are advised to use the `zod` package,
as it provides various critical features out of the box. Constraints to be followed when developing
a HTTP model is placed within `docs/architecture/Models.md`

## Schema & Persistence
The native supabase client is the default database access layer, An ORM or quer builder may be introduced
only when the native client cannot adequately support a document requirement. If an ORM os introduced,
its migration and schema ownership resposiblities must be explicitely defined.

All changes in chema must be handled through migrations (possibly supabase handled). Further documentation
shall be referred from `docs/architecture/Schema.md`

# UI/UX
The default UI/UX design framework is Next.js(latest release version), design should strictly follow up
with the vetted and collectively decided desing, and any change shall be accounted for, and resonated.
Design is recommended to be accomplished using tailwindcss for simplicity and readiness of the design
framework. It is encouraged to design and develop reusable and centrally configured components
which allows us the change the design app wide without further hustle and time consumption.

All UI/UX components shall reside in the `src/` directory. And the overall app ui should reside in
`app/` directory.

# Development Constraints
The following general conditions are to be followed for the smooth execution of the project.
- Do not use pre-release version of frameworks.
- Do not implement features or modules without logs or which doesn't support logging
- Do use the latest stable version of packages and modules
- Update dependencies regularly and proper security audit is to be conducted whenever possible.
- Merge conflicts are to be resolved within 24 hours of conflict detection inorder to facilitate
  other team members to work along seamlessly.
- Any change of plans should be notified to the team, prior to applying or implementing the change
- When automating, manually verify the work done that it follows and considers our code aesthetics.
