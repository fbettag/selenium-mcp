{{/*
Expand the name of the chart.
*/}}
{{- define "selenium-mcp.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "selenium-mcp.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "selenium-mcp.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "selenium-mcp.labels" -}}
helm.sh/chart: {{ include "selenium-mcp.chart" . }}
{{ include "selenium-mcp.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "selenium-mcp.selectorLabels" -}}
app.kubernetes.io/name: {{ include "selenium-mcp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "selenium-mcp.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "selenium-mcp.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Get browserless URL
*/}}
{{- define "selenium-mcp.browserlessUrl" -}}
{{- if .Values.browserless.enabled }}
{{- printf "http://%s-browserless:%d" .Release.Name .Values.browserless.service.port }}
{{- else }}
{{- if .Values.browserless.service.existingServiceNamespace }}
{{- printf "http://%s.%s.svc.cluster.local:%d" .Values.browserless.service.existingService .Values.browserless.service.existingServiceNamespace .Values.browserless.service.port }}
{{- else }}
{{- printf "http://%s:%d" .Values.browserless.service.existingService .Values.browserless.service.port }}
{{- end }}
{{- end }}
{{- end }}