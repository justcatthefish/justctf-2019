#include <LiquidCrystal.h>
LiquidCrystal lcd(2, 3, 4, 5, 6, 7);

void setup() {
  lcd.clear();
  delay(500);
  lcd.begin(20, 4);
  lcd.setCursor(0, 0);
  lcd.print("justCTF{");
  lcd.setCursor(2, 1);
  lcd.print("0ld_5ch00l_LDC_");
  lcd.setCursor(2, 2);
  lcd.print("d15pl4y5_4r3_c00l");
  lcd.setCursor(19, 4);
  lcd.print("}");
}

void loop() {
}