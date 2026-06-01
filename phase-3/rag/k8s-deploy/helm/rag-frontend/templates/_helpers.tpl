{{- define "rag-frontend.name" -}}
{{- .Chart.Name }}
{{- end }}

{{- define "rag-frontend.labels" -}}
app: rag-ui
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
