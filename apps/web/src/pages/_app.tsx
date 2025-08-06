import '@/styles/globals.css'
import type { AppProps } from 'next/app'
import Layout from '@/components/Layout'
import { PromptProvider } from '@/contexts/PromptContext'
import { LookupProvider } from '@/contexts/LookupContext'

export default function App({ Component, pageProps }: AppProps) {
  return (
    <PromptProvider>
      <LookupProvider>
        <Layout>
          <Component {...pageProps} />
        </Layout>
      </LookupProvider>
    </PromptProvider>
  )
}
