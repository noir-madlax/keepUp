import { createClient } from '@supabase/supabase-js'
import dotenv from 'dotenv'

dotenv.config()

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
)

async function test() {
  console.log('Testing Supabase connection...\n')
  
  // Test 1: List websites
  console.log('1. Querying websites table:')
  const { data: websites, error: websitesError } = await supabase
    .from('websites')
    .select('slug, name')
  
  if (websitesError) {
    console.error('  Error:', websitesError)
  } else {
    console.log('  Found', websites?.length || 0, 'websites:')
    websites?.forEach(w => console.log(`    - ${w.slug}: ${w.name}`))
  }
  
  // Test 2: List cookies
  console.log('\n2. Querying cookies table:')
  const { data: cookies, error: cookiesError } = await supabase
    .from('cookies')
    .select('site_slug, is_valid')
  
  if (cookiesError) {
    console.error('  Error:', cookiesError)
  } else {
    console.log('  Found', cookies?.length || 0, 'cookie records:')
    cookies?.forEach(c => console.log(`    - ${c.site_slug}: valid=${c.is_valid}`))
  }
  
  // Test 3: List scraped_data
  console.log('\n3. Querying scraped_data table:')
  const { data: scrapedData, error: scrapedError } = await supabase
    .from('scraped_data')
    .select('site_slug, created_at')
    .order('created_at', { ascending: false })
    .limit(5)
  
  if (scrapedError) {
    console.error('  Error:', scrapedError)
  } else {
    console.log('  Found', scrapedData?.length || 0, 'scraped data records:')
    scrapedData?.forEach(d => console.log(`    - ${d.site_slug}: ${d.created_at}`))
  }
}

test().catch(console.error)

