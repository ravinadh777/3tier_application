
Skip to content
NIS-Guyana
citizen-identity-portal-api
Repository navigation
Code
Issues
Pull requests
Agents
Actions
Projects
Security and quality
Insights
Settings
Citizen Identity Portal API - UAT RTF CI/CD
Fix YAML syntax for workflow name #30
All jobs
Run details
Workflow file for this run
.github/workflows/rtf-uat.yml at 08c0d46
name: Citizen Identity Portal API - UAT RTF CI/CD

on:
  push:
    branches:
      - UAT
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: citizen-identity-portal-api-uat
  cancel-in-progress: false

jobs:

  # ============================================================
  # BUILD & TEST
  # ============================================================

  build:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:

      - name: Checkout Citizen Identity Portal API
        uses: actions/checkout@v4
        with:
          fetch-depth: 1

      - name: Setup Java 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: temurin
          cache: maven

      # Pin Maven 3.9.9 - the runner's default Maven is not compatible
      # with mule-maven-plugin 4.9.x (NoSuchMethodError DefaultMirrorSelector.add)
      - name: Setup Maven 3.9.9
        shell: bash
        run: |
          set -e
          MVN_VERSION=3.9.9
          curl -fsSL "https://archive.apache.org/dist/maven/maven-3/${MVN_VERSION}/binaries/apache-maven-${MVN_VERSION}-bin.tar.gz" \
            | tar -xz -C "$HOME"
          echo "$HOME/apache-maven-${MVN_VERSION}/bin" >> "$GITHUB_PATH"
      - name: Verify Java and Maven
        run: |
          java -version
          mvn -version
      - name: Build and Test Citizen Identity Portal API
        shell: bash
        run: |
          set -e
          mvn clean package -DskipMunitTests
      - name: Verify Build Output
        shell: bash
        run: |
          set -e
          ls -lh target
          JAR_COUNT=$(find target -maxdepth 1 -type f -name "*.jar" | wc -l)
          if [ "$JAR_COUNT" -eq 0 ]; then
            echo "::error::No Mule application JAR found."
            exit 1
          fi
          find target -maxdepth 1 -type f -name "*.jar" -exec ls -lh {} \;
  # ============================================================
  # DEPLOY TO UAT RUNTIME FABRIC
  # ============================================================

  deploy-uat:
    needs: build
    runs-on: ubuntu-latest
    timeout-minutes: 30
    environment: UAT
    if: github.ref_name == 'UAT'

    env:
      ANYPOINT_CLIENT_ID: ${{ secrets.ANYPOINT_CLIENT_ID }}
      ANYPOINT_CLIENT_SECRET: ${{ secrets.ANYPOINT_CLIENT_SECRET }}
      ANYPOINT_BUSINESS_GROUP_ID: ${{ secrets.ANYPOINT_BUSINESS_GROUP_ID }}
      ANYPOINT_ORG_ID: ${{ secrets.ANYPOINT_ORG_ID }}
      ANYPOINT_ENV_ID: ${{ secrets.ANYPOINT_ENV_ID }}
      ANYPOINT_GRANT_TYPE: ${{ secrets.ANYPOINT_GRANT_TYPE }}
      RTF_TARGET: ${{ secrets.RTF_TARGET }}
      ANYPOINT_ENVIRONMENT: UAT

    steps:

      - name: Checkout Citizen Identity Portal API
        uses: actions/checkout@v4

      - name: Setup Java 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: temurin
          cache: maven

      - name: Setup Maven 3.9.9
        shell: bash
        run: |
          set -e
          MVN_VERSION=3.9.9
          curl -fsSL "https://archive.apache.org/dist/maven/maven-3/${MVN_VERSION}/binaries/apache-maven-${MVN_VERSION}-bin.tar.gz" \
            | tar -xz -C "$HOME"
          echo "$HOME/apache-maven-${MVN_VERSION}/bin" >> "$GITHUB_PATH"
      - name: Verify Maven
        run: mvn -version

      - name: Verify Required UAT Secrets
        shell: bash
        run: |
          set -e
          missing=0
          for v in \
            ANYPOINT_CLIENT_ID ANYPOINT_CLIENT_SECRET ANYPOINT_BUSINESS_GROUP_ID \
            ANYPOINT_ORG_ID ANYPOINT_ENV_ID ANYPOINT_GRANT_TYPE RTF_TARGET
          do
            if [ -z "${!v}" ]; then
              echo "::error::$v is missing or empty"; missing=1
            else
              echo "$v is set"
            fi
          done
          [ "$missing" -eq 0 ] || exit 1
      - name: Verify Anypoint OAuth credentials
        shell: bash
        run: |
          set -e
          HTTP_STATUS=$(curl -sS -o /tmp/anypoint-oauth-response.json -w "%{http_code}" \
            -X POST "https://anypoint.mulesoft.com/accounts/api/v2/oauth2/token" \
            -H "Content-Type: application/x-www-form-urlencoded" \
            --data-urlencode "client_id=${ANYPOINT_CLIENT_ID}" \
            --data-urlencode "client_secret=${ANYPOINT_CLIENT_SECRET}" \
            --data-urlencode "grant_type=${ANYPOINT_GRANT_TYPE}")
          echo "Anypoint OAuth HTTP status: ${HTTP_STATUS}"
          if [ "${HTTP_STATUS}" != "200" ]; then
            echo "::error::Anypoint OAuth authentication failed."
            cat /tmp/anypoint-oauth-response.json
            exit 1
          fi
      - name: Generate Maven Settings
        shell: bash
        run: |
          set -e
          mkdir -p "$HOME/.m2"
          cat > "$HOME/.m2/settings.xml" <<MAVEN_SETTINGS
          <?xml version="1.0" encoding="UTF-8"?>
          <settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                    xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0
                    https://maven.apache.org/xsd/settings-1.0.0.xsd">
            <servers>
              <server>
                <id>anypoint-exchange-v3</id>
                <username>~~~Client~~~</username>
                <password>${ANYPOINT_CLIENT_ID}~?~${ANYPOINT_CLIENT_SECRET}</password>
              </server>
              <server>
                <id>anypoint-exchange</id>
                <username>~~~Client~~~</username>
                <password>${ANYPOINT_CLIENT_ID}~?~${ANYPOINT_CLIENT_SECRET}</password>
              </server>
              <server>
                <id>mulesoft-releases</id>
                <username>~~~Client~~~</username>
                <password>${ANYPOINT_CLIENT_ID}~?~${ANYPOINT_CLIENT_SECRET}</password>
              </server>
            </servers>
          </settings>
          MAVEN_SETTINGS
          chmod 600 "$HOME/.m2/settings.xml"
      # UAT uses 1.1.x so it never collides with staging's 1.0.x
      - name: Set Application Version
        shell: bash
        run: |
          set -e
          NEW_VERSION="1.1.${{ github.run_number }}"
          mvn versions:set -DnewVersion="$NEW_VERSION" -DgenerateBackupPoms=false
          echo "APP_VERSION=$NEW_VERSION" >> "$GITHUB_ENV"
      - name: Verify POM Configuration
        run: |
          grep -nE '<groupId>|<artifactId>|<version>|<businessGroupId>|<target>|<environment>' pom.xml
      # Step 1: build and publish the new version to Anypoint Exchange.
      # (No -DmuleDeploy here, so mule:deploy is skipped.)
      - name: Publish to Anypoint Exchange
        shell: bash
        run: |
          set -e
          mvn clean deploy -DskipTests -DskipMunitTests -e
      # Step 2: deploy that version to Runtime Fabric.
      # Run ONLY the mule:deploy goal (no "package"/lifecycle phases), so the
      # Exchange pre-deploy check does not run again and fail with
      # "asset already exists". The JAR built in step 1 is reused.
      - name: Deploy to UAT Runtime Fabric
        shell: bash
        run: |
          set -e
          ARTIFACT="target/citizen-identity-portal-api-${APP_VERSION}-mule-application.jar"
          if [ ! -f "$ARTIFACT" ]; then
            echo "::error::Expected artifact not found: $ARTIFACT"
            ls -lh target
            exit 1
          fi
          mvn mule:deploy -DmuleDeploy -Dmule.artifact="$ARTIFACT" -e
      - name: Deployment Completed
        run: echo "NIS Citizen Identity Portal API ${APP_VERSION} deployed to UAT."
