<script>
	// Mesmas importações do layout padrão do Evidence: sem elas o site perde o Tailwind
	import '@evidence-dev/tailwind/fonts.css';
	import '../app.css';
	import { EvidenceDefaultLayout } from '@evidence-dev/core-components';
	export let data;
</script>

<EvidenceDefaultLayout
	{data}
	title="Geração Solar no Brasil"
	homePageName="Visão geral"
	githubRepo="https://github.com/vitorsarilio/geracao-solar-brasil"
	neverShowQueries={false}
	maxWidth={1280}
>
	<slot slot="content" />
</EvidenceDefaultLayout>
