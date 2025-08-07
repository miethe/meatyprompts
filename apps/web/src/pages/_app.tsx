import '@/styles/globals.css'
import type { AppProps } from 'next/app'
import Layout from '@/components/Layout'
import { PromptProvider } from '@/contexts/PromptContext'
import { LookupProvider } from '@/contexts/LookupContext'
import { FieldHelpProvider } from '@/contexts/FieldHelpContext'

export default function App({ Component, pageProps }: AppProps) {
  return (
    <PromptProvider>
      <LookupProvider>
        <FieldHelpProvider>
          <Layout>
            <Component {...pageProps} />
          </Layout>
        </FieldHelpProvider>
      </LookupProvider>
    </PromptProvider>
  )
}
