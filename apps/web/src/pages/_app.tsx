import '@/styles/globals.css'
import '@/i18n';
import type { AppProps } from 'next/app'
import Layout from '@/components/Layout'
import { PromptProvider } from '@/contexts/PromptContext'
import { LookupProvider } from '@/contexts/LookupContext'
import { FieldHelpProvider } from '@/contexts/FieldHelpContext'
import { ThemeProvider } from '@/theme'

export default function App({ Component, pageProps }: AppProps) {
  return (
    <ThemeProvider>
      <PromptProvider>
        <LookupProvider>
          <FieldHelpProvider>
            <Layout>
              <Component {...pageProps} />
            </Layout>
          </FieldHelpProvider>
        </LookupProvider>
      </PromptProvider>
    </ThemeProvider>
  )
}
