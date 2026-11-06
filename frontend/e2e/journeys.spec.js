import { expect, test } from '@playwright/test'

test.describe('core journeys', () => {
  test('home search by English, Tamil and Thanglish', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByRole('heading', { name: 'AgroSeason AI' })).toBeVisible()
    for (const q of ['Tomato', 'தக்காளி', 'Thakkali']) {
      const box = page.getByRole('combobox', { name: 'Crop' })
      await box.fill('')
      await box.fill(q)
      await expect(page.getByRole('listbox').getByRole('option').first()).toContainText('Tomato')
    }
  })

  test('tomato + Salem + November shows documented window, guide and sketch', async ({ page }) => {
    await page.goto('/')
    await page.getByLabel('District', { exact: true }).selectOption({ label: 'Salem' })
    await page.getByLabel('Month', { exact: true }).selectOption({ label: 'November' })
    await page.getByRole('combobox', { name: 'Crop' }).fill('Thakkali')
    await page.getByRole('listbox').getByRole('option').first().click()
    await expect(page).toHaveURL(/\/crops\/\d+\?district=\d+&month=11/)
    await expect(page.getByRole('heading', { name: 'Tomato', level: 1 })).toBeVisible()
    await expect(page.getByTestId('month-banner')).toContainText('November is a documented sowing month')
    await expect(page.getByTestId('cell-sowing-11')).toHaveAttribute('data-active', 'true')
    await expect(page.getByTestId('cell-harvest-2')).toHaveAttribute('data-active', 'true')
    await expect(page.getByText('TEST FIXTURE soil text')).toBeVisible()
    await expect(page.getByText('Insufficient verified information.').first()).toBeVisible()
    const img = page.getByRole('img', { name: /Pencil sketch/ })
    await expect(img).toBeVisible()
    await expect.poll(() => img.evaluate((i) => i.naturalWidth)).toBeGreaterThan(0)
    await expect(page.getByText(/CC BY-SA 4.0/).first()).toBeVisible()
  })

  test('month with no record is reported honestly', async ({ page }) => {
    await page.goto('/crops?q=tomato')
    await page.getByRole('link', { name: /Tomato/ }).first().click()
    await page.getByLabel('District', { exact: true }).selectOption({ label: 'Salem' })
    await page.getByLabel('Month', { exact: true }).selectOption({ label: 'June' })
    await expect(page.getByTestId('month-banner')).toContainText('no documented sowing window')
  })

  test('catalog filter and pagination', async ({ page }) => {
    await page.goto('/crops')
    await expect(page.getByRole('list').getByRole('link').first()).toBeVisible()
    await page.getByRole('button', { name: 'Millets' }).click()
    await expect(page.getByRole('link', { name: /Finger Millet/ })).toBeVisible()
    await expect(page.getByRole('link', { name: /Tomato/ })).toHaveCount(0)
    await page.getByRole('button', { name: 'All', exact: true }).click()
    await page.getByRole('button', { name: 'Next' }).click()
    await expect(page.getByText(/Page 2/)).toBeVisible()
  })

  test('district explorer lists 38 districts and district crops', async ({ page }) => {
    await page.goto('/districts')
    await expect(page.locator('main ul li a')).toHaveCount(38)
    await page.getByRole('link', { name: /Salem/ }).click()
    await expect(page.getByRole('link', { name: /Tomato/ })).toBeVisible()
    await page.getByLabel('Month', { exact: true }).selectOption({ label: 'March' })
    await expect(page.getByText('Insufficient verified information.').first()).toBeVisible()
  })

  test('farming calendar renders and month selection works', async ({ page }) => {
    await page.goto('/calendar')
    await page.getByLabel('Crop').selectOption({ label: 'Tomato' })
    await page.getByLabel('District', { exact: true }).selectOption({ label: 'Salem' })
    await expect(page.getByRole('table')).toBeVisible()
    await expect(page.getByTestId('suit-10')).toHaveAttribute('data-suitability', 'recommended')
    await expect(page.getByTestId('suit-6')).toHaveAttribute('data-suitability', 'not_documented')
    await page.getByRole('button', { name: 'October' }).click()
    await expect(page.getByRole('status').filter({ hasText: 'October' })).toContainText(/verified/i)
  })

  test('paddy sample seasons are flagged unverified with cross-year sowing', async ({ page }) => {
    await page.goto('/calendar')
    await page.getByLabel('Crop').selectOption({ label: 'Paddy (Rice)' })
    await expect(page.getByTestId('suit-1')).toHaveAttribute('data-suitability', 'documented_unverified')
    await expect(page.getByTestId('suit-12')).toHaveAttribute('data-suitability', 'documented_unverified')
  })

  test('language switching persists and translates', async ({ page }) => {
    await page.goto('/')
    await page.getByRole('button', { name: 'தமிழ்' }).click()
    await expect(page.getByRole('heading', { name: 'அக்ரோசீசன் AI' })).toBeVisible()
    await page.getByRole('link', { name: 'மாவட்டங்கள்' }).click()
    await expect(page.getByRole('link', { name: /சேலம்/ })).toBeVisible()
    await page.reload()
    await expect(page.getByRole('link', { name: 'மாவட்டங்கள்' })).toBeVisible()
    await page.getByRole('link', { name: 'மொழி' }).click()
    await page.getByLabel('English').check()
    await expect(page.getByRole('heading', { name: 'Language' })).toBeVisible()
  })

  test('research request creates a tracked job (no keys configured, no paid calls)', async ({ page }) => {
    await page.goto('/crops?q=pumpkin')
    await page.getByRole('link', { name: /Pumpkin/ }).first().click()
    await page.getByRole('button', { name: 'Request research' }).click()
    await expect(page.getByTestId('job-status')).toBeVisible()
    await page.goto('/research')
    await expect(page.getByTestId('job-card').first()).toBeVisible()
    await expect(page.getByText('Not configured').first()).toBeVisible()
  })

  test('only two colours are used in rendered UI', async ({ page }) => {
    await page.goto('/')
    const colours = await page.evaluate(() => {
      const set = new Set()
      document.querySelectorAll('body *').forEach((el) => {
        const s = getComputedStyle(el)
        for (const p of ['color', 'backgroundColor', 'borderTopColor']) {
          const v = s[p]
          if (v && !v.startsWith('rgba(0, 0, 0, 0)')) set.add(v.replace(/, 0\.\d+\)/, ')').replace('rgba', 'rgb'))
        }
        if (s.backgroundImage !== 'none') set.add('IMAGE:' + s.backgroundImage.slice(0, 20))
      })
      return [...set]
    })
    const allowed = new Set(['rgb(22, 101, 52)', 'rgb(255, 255, 255)'])
    expect(colours.filter((c) => !allowed.has(c) && !c.startsWith('IMAGE:url'))).toEqual([])
    expect(colours.filter((c) => c.includes('gradient'))).toEqual([])
  })

  test('keyboard: skip link and suggestion navigation @a11y', async ({ page }) => {
    await page.goto('/')
    await page.keyboard.press('Tab')
    await expect(page.getByRole('link', { name: 'Skip to content' })).toBeFocused()
    await page.getByRole('combobox', { name: 'Crop' }).fill('okra')
    await page.getByRole('listbox').getByRole('option').first().waitFor()
    await page.keyboard.press('ArrowDown')
    await page.keyboard.press('Enter')
    await expect(page).toHaveURL(/\/crops\/\d+/)
  })

  test('mobile layout is usable @mobile', async ({ page }) => {
    await page.goto('/')
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1)
    expect(overflow).toBe(false)
    await page.getByRole('combobox', { name: 'Crop' }).fill('tomato')
    await page.getByRole('listbox').getByRole('option').first().click()
    await expect(page.getByRole('heading', { name: 'Tomato', level: 1 })).toBeVisible()
    const overflow2 = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1)
    expect(overflow2).toBe(false)
  })
})
