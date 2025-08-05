import '@/styles/globals.css'
import type { AppProps } from 'next/app'
import Layout from '@/components/Layout'
import { PromptProvider } from '@/contexts/PromptContext'

export default function App({ Component, pageProps }: AppProps) {
  return (
    <PromptProvider>
      <Layout>
        <Component {...pageProps} />
      </Layout>
    </PromptProvider>
  )
}
