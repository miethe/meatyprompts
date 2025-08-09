import '@/styles/globals.css'
import '@/i18n';
import type { AppProps } from 'next/app'
import Layout from '@/components/Layout'
import { PromptProvider } from '@/contexts/PromptContext'
import { LookupProvider } from '@/contexts/LookupContext'
import { FieldHelpProvider } from '@/contexts/FieldHelpContext'
import { ThemeProvider } from '@/theme'
import { ClerkProvider } from '@clerk/nextjs'

export default function App({ Component, pageProps }: AppProps) {
  return (
    <ClerkProvider {...pageProps}>
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
    </ClerkProvider>
  )
}
