import 'package:flutter_test/flutter_test.dart';
import 'package:ephemeral_client/main.dart';

void main() {
  testWidgets('EphemeralApp smoke test renders home title', (WidgetTester tester) async {
    await tester.pumpWidget(const EphemeralApp());

    expect(find.text('Ephemeral — UD-Chat E2EE'), findsOneWidget);
    expect(find.text('Ephemeral Messaging'), findsOneWidget);
  });
}
